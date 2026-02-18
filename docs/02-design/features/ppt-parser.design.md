# Design: ppt-parser

> PPT 파일에서 텍스트, 이미지, 테이블을 추출하는 파서 모듈 설계서

## 1. Overview

| Item | Description |
|------|-------------|
| Feature Name | ppt-parser |
| Plan Document | [ppt-parser.plan.md](../../01-plan/features/ppt-parser.plan.md) |
| Status | Design |
| Created | 2026-02-18 |

## 2. Architecture

### 2.1 Module Structure

```
modules/
└── parser.py           # PPT 파싱 모듈 (단일 파일 유지)
    ├── Core Functions  # 핵심 추출 기능
    ├── Helper Functions # 보조 함수
    └── Error Handling  # 에러 처리 유틸리티
```

### 2.2 Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Streamlit   │────▶│ parser.py    │────▶│ SlideContent    │
│ UploadedFile│     │              │     │ (Dict)          │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ generator.py │
                    │ chatbot.py   │
                    └──────────────┘
```

## 3. Data Models

### 3.1 SlideContent (기존 유지 + 확장)

```python
SlideContent = TypedDict('SlideContent', {
    # 기존 필드 (유지)
    'slide_num': int,           # 슬라이드 번호 (1부터 시작)
    'texts': List[str],         # 추출된 텍스트 목록
    'images': List[ImageData],  # 추출된 이미지 목록
    'tables': List[TableData],  # 추출된 테이블 목록
    'has_chart': bool,          # 차트 존재 여부
    'has_diagram': bool,        # 다이어그램 존재 여부

    # 신규 필드 (FR-06)
    'notes': Optional[str],     # 발표자 노트 (NEW)

    # 신규 필드 (에러 추적)
    'parse_errors': List[str],  # 파싱 중 발생한 에러 목록 (NEW)
})
```

### 3.2 ImageData (기존 유지)

```python
ImageData = TypedDict('ImageData', {
    'base64': str,              # Base64 인코딩된 이미지
    'format': str,              # 파일 확장자 (png, jpg 등)
    'width': Optional[float],   # 너비 (inches)
    'height': Optional[float],  # 높이 (inches)
    'media_type': str,          # MIME 타입
})
```

### 3.3 TableData (기존 유지)

```python
TableData = List[List[str]]     # 2차원 문자열 배열
```

### 3.4 ParseResult (신규 - 전체 결과 래퍼)

```python
ParseResult = TypedDict('ParseResult', {
    'slides': List[SlideContent],  # 슬라이드 데이터 목록
    'metadata': ParseMetadata,      # 파싱 메타데이터
    'success': bool,                # 전체 성공 여부
    'errors': List[str],            # 전체 에러 목록
})

ParseMetadata = TypedDict('ParseMetadata', {
    'total_slides': int,            # 전체 슬라이드 수
    'parsed_slides': int,           # 성공적으로 파싱된 슬라이드 수
    'total_images': int,            # 전체 이미지 수
    'total_tables': int,            # 전체 테이블 수
    'has_notes': bool,              # 발표자 노트 존재 여부
    'parse_time_ms': float,         # 파싱 소요 시간 (밀리초)
})
```

## 4. Function Specifications

### 4.1 Core Functions

#### 4.1.1 extract_slide_content (기존 수정)

```python
def extract_slide_content(
    uploaded_file: Union[BinaryIO, UploadedFile],
    include_notes: bool = True,
    skip_on_error: bool = True
) -> List[SlideContent]:
    """
    PPT 파일에서 모든 슬라이드 콘텐츠를 추출합니다.

    Args:
        uploaded_file: Streamlit UploadedFile 또는 파일 객체
        include_notes: 발표자 노트 포함 여부 (기본: True)
        skip_on_error: 에러 발생 시 해당 슬라이드 스킵 (기본: True)

    Returns:
        List[SlideContent]: 슬라이드별 추출된 콘텐츠

    Raises:
        PPTParseError: skip_on_error=False일 때 파싱 실패 시

    Example:
        >>> slides = extract_slide_content(uploaded_file)
        >>> print(f"Total slides: {len(slides)}")
    """
```

**구현 변경사항:**
- 슬라이드별 try-except 래핑 추가
- `notes` 필드 추출 로직 추가
- `parse_errors` 필드에 에러 기록

#### 4.1.2 extract_notes (신규)

```python
def extract_notes(slide: Slide) -> Optional[str]:
    """
    슬라이드의 발표자 노트를 추출합니다.

    Args:
        slide: python-pptx Slide 객체

    Returns:
        Optional[str]: 발표자 노트 텍스트 또는 None

    Example:
        >>> notes = extract_notes(slide)
        >>> if notes:
        ...     print(f"Notes: {notes[:100]}...")
    """
```

**구현 로직:**
```python
try:
    notes_slide = slide.notes_slide
    if notes_slide and notes_slide.notes_text_frame:
        return notes_slide.notes_text_frame.text.strip() or None
except Exception:
    return None
return None
```

#### 4.1.3 extract_image (기존 유지)

```python
def extract_image(shape: Shape) -> Optional[ImageData]:
    """
    Shape에서 이미지를 추출하고 Base64로 변환합니다.

    Args:
        shape: python-pptx Shape 객체

    Returns:
        Optional[ImageData]: 이미지 데이터 또는 None (추출 실패 시)
    """
```

**변경사항 없음** - 현재 구현 유지

#### 4.1.4 extract_table (기존 유지)

```python
def extract_table(table: Table) -> TableData:
    """
    테이블 콘텐츠를 2차원 배열로 추출합니다.

    Args:
        table: python-pptx Table 객체

    Returns:
        TableData: 2차원 문자열 배열
    """
```

**변경사항 없음** - 현재 구현 유지

### 4.2 Helper Functions

#### 4.2.1 get_media_type (기존 유지)

```python
def get_media_type(ext: str) -> str:
    """파일 확장자에서 MIME 타입 반환"""
```

#### 4.2.2 get_slide_text_combined (기존 수정)

```python
def get_slide_text_combined(
    slide_data: SlideContent,
    include_notes: bool = False
) -> str:
    """
    슬라이드의 모든 텍스트를 하나의 문자열로 결합합니다.

    Args:
        slide_data: SlideContent 딕셔너리
        include_notes: 발표자 노트 포함 여부 (기본: False)

    Returns:
        str: 결합된 텍스트
    """
```

**변경사항:**
- `include_notes` 파라미터 추가
- 발표자 노트를 `[발표자 노트]` 섹션으로 추가

#### 4.2.3 get_all_text_content (기존 유지)

```python
def get_all_text_content(slides_data: List[SlideContent]) -> str:
    """모든 슬라이드의 텍스트를 하나의 문자열로 반환"""
```

#### 4.2.4 get_slides_with_images (기존 유지)

```python
def get_slides_with_images(slides_data: List[SlideContent]) -> List[SlideContent]:
    """이미지가 포함된 슬라이드만 필터링"""
```

#### 4.2.5 prepare_vision_content (기존 유지)

```python
def prepare_vision_content(slide_data: SlideContent) -> List[Dict[str, Any]]:
    """Claude Vision API용 콘텐츠 블록 준비"""
```

### 4.3 Error Handling

#### 4.3.1 PPTParseError (신규)

```python
class PPTParseError(Exception):
    """PPT 파싱 관련 커스텀 예외"""

    def __init__(self, message: str, slide_num: Optional[int] = None):
        self.message = message
        self.slide_num = slide_num
        super().__init__(self.message)
```

## 5. Implementation Order

### Phase 1: 에러 핸들링 강화 (Priority: High)
1. [ ] `PPTParseError` 예외 클래스 추가
2. [ ] `extract_slide_content`에 슬라이드별 try-except 추가
3. [ ] `parse_errors` 필드 추가 및 에러 기록

### Phase 2: 발표자 노트 추출 (Priority: Medium)
4. [ ] `extract_notes` 함수 구현
5. [ ] `SlideContent`에 `notes` 필드 추가
6. [ ] `extract_slide_content`에서 노트 추출 호출

### Phase 3: 유틸리티 개선 (Priority: Low)
7. [ ] `get_slide_text_combined`에 `include_notes` 파라미터 추가
8. [ ] 로깅 추가 (선택적)

## 6. Error Handling Strategy

### 6.1 에러 레벨

| Level | Handling | Example |
|-------|----------|---------|
| Critical | 전체 중단 | 파일 열기 실패, 잘못된 형식 |
| Slide | 슬라이드 스킵 | 개별 슬라이드 손상 |
| Shape | Shape 스킵 | 이미지 추출 실패 |

### 6.2 에러 복구 플로우

```
파일 열기 시도
├── 실패 → PPTParseError 발생 (Critical)
└── 성공 → 슬라이드 순회
            ├── 슬라이드 파싱 실패 → parse_errors에 기록, 다음 슬라이드로
            └── 슬라이드 파싱 성공
                ├── Shape 처리 실패 → 로그 기록, 다음 Shape로
                └── Shape 처리 성공 → 데이터 추가
```

## 7. Testing Strategy

### 7.1 테스트 케이스

| ID | Test Case | Input | Expected |
|----|-----------|-------|----------|
| TC-01 | 정상 PPT 파싱 | 일반 .pptx | 모든 슬라이드 추출 |
| TC-02 | 빈 슬라이드 처리 | 빈 슬라이드 포함 PPT | 빈 texts/images 반환 |
| TC-03 | 이미지 추출 | 이미지 포함 PPT | Base64 이미지 데이터 |
| TC-04 | 테이블 추출 | 테이블 포함 PPT | 2D 배열 데이터 |
| TC-05 | 발표자 노트 | 노트 포함 PPT | notes 필드에 텍스트 |
| TC-06 | 손상된 슬라이드 | 일부 손상 PPT | 정상 슬라이드만 추출, 에러 기록 |
| TC-07 | 대용량 파일 | 100+ 슬라이드 | 30초 이내 완료 |

### 7.2 테스트 방법

- Zero Script QA: 실제 PPT 파일로 수동 테스트
- 로그 기반 검증: 파싱 결과 로깅 후 확인

## 8. Backward Compatibility

### 8.1 기존 API 호환성

| Function | Change | Compatibility |
|----------|--------|---------------|
| `extract_slide_content` | 신규 필드 추가 | ✅ 호환 (추가 필드는 선택적) |
| `extract_image` | 변경 없음 | ✅ 호환 |
| `extract_table` | 변경 없음 | ✅ 호환 |
| `get_slide_text_combined` | 파라미터 추가 | ✅ 호환 (기본값 사용) |
| 기타 함수 | 변경 없음 | ✅ 호환 |

### 8.2 소비자 코드 영향

- `app.py`: 변경 불필요 (기존 필드만 사용)
- `generator.py`: 변경 불필요
- `chatbot.py`: 변경 불필요

## 9. Dependencies

### 9.1 추가 의존성

없음 - 기존 의존성만 사용

### 9.2 기존 의존성

```python
# requirements.txt (변경 없음)
python-pptx>=1.0.2
Pillow>=10.0.0
```

## 10. File Changes Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `modules/parser.py` | Modify | 에러 핸들링, 노트 추출 추가 |

## 11. Next Steps

1. [x] Design 문서 완료
2. [ ] 구현 시작 (`/pdca do ppt-parser`)
3. [ ] Gap 분석 (`/pdca analyze ppt-parser`)

---

*Document generated by bkit PDCA*
