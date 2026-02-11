# PDCA Workflow Guide

PPT Study Assistant 프로젝트의 PDCA 기반 개발 워크플로우 가이드입니다.

---

## PDCA 사이클 개요

```
[Plan] → [Design] → [Do] → [Check] → [Act]
  계획      설계      구현     검증      개선
```

| Phase | 목적 | 산출물 |
|-------|------|--------|
| **Plan** | 요구사항 정의, 범위 설정 | `{feature}.plan.md` |
| **Design** | 기술 설계, 아키텍처 결정 | `{feature}.design.md` |
| **Do** | 구현 | 코드, 테스트 |
| **Check** | 설계-구현 Gap 분석 | `{feature}.analysis.md` |
| **Act** | 회고, 개선사항 정리 | `{feature}.report.md` |

---

## 디렉토리 구조

```
docs/
├── PDCA-WORKFLOW.md          # 이 가이드
├── 01-plan/                  # Plan 단계 문서
│   └── features/             # 기능별 계획 문서
│       └── {feature}.plan.md
├── 02-design/                # Design 단계 문서
│   └── features/             # 기능별 설계 문서
│       └── {feature}.design.md
├── 03-check/                 # Check 단계 문서
│   └── {feature}.analysis.md
└── 04-act/                   # Act 단계 문서
    └── {feature}.report.md
```

---

## 워크플로우 사용법

### 1. Plan (계획)

새 기능 개발 시작 시:

```
/pdca plan {기능명}
```

**체크리스트:**
- [ ] 기능의 목적과 배경 정의
- [ ] 범위 (In/Out of Scope) 명확화
- [ ] 기능/비기능 요구사항 정리
- [ ] 성공 기준 정의
- [ ] 리스크 식별

**산출물:** `docs/01-plan/features/{feature}.plan.md`

---

### 2. Design (설계)

Plan 완료 후:

```
/pdca design {기능명}
```

**체크리스트:**
- [ ] 아키텍처 다이어그램 작성
- [ ] 데이터 모델 정의
- [ ] API 명세 (해당 시)
- [ ] UI/UX 설계 (해당 시)
- [ ] 에러 처리 전략
- [ ] 테스트 계획

**산출물:** `docs/02-design/features/{feature}.design.md`

---

### 3. Do (구현)

Design 완료 후:

```
/pdca do {기능명}
```

**체크리스트:**
- [ ] 설계 문서 참조하며 구현
- [ ] 코딩 컨벤션 준수
- [ ] 에러 처리 구현
- [ ] 기본 테스트 수행

**산출물:** 코드

---

### 4. Check (검증)

구현 완료 후:

```
/pdca analyze {기능명}
```

**체크리스트:**
- [ ] 설계 vs 구현 Gap 분석
- [ ] 코드 품질 검토
- [ ] 보안 이슈 점검
- [ ] 테스트 커버리지 확인

**산출물:** `docs/03-check/{feature}.analysis.md`

---

### 5. Act (개선)

Check 완료 후:

```
/pdca report {기능명}
```

**체크리스트:**
- [ ] 완료 항목 정리
- [ ] 미완료 항목 및 사유
- [ ] 품질 메트릭 최종 정리
- [ ] 회고 (Keep/Problem/Try)
- [ ] 다음 사이클 계획

**산출물:** `docs/04-act/{feature}.report.md`

---

## 프로젝트 레벨

이 프로젝트는 **Starter** 레벨로 분류됩니다:

| Level | 특징 | 구조 |
|-------|------|------|
| **Starter** (현재) | 단순한 구조, 빠른 개발 | `modules/`, `app.py` |
| Dynamic | 기능 기반 모듈화, BaaS 연동 | `features/`, `services/` |
| Enterprise | 계층 분리, DI, 마이크로서비스 | `presentation/`, `domain/` |

---

## Quick Reference

| 작업 | 명령어 |
|------|--------|
| 계획 시작 | `/pdca plan {feature}` |
| 설계 시작 | `/pdca design {feature}` |
| 구현 가이드 | `/pdca do {feature}` |
| Gap 분석 | `/pdca analyze {feature}` |
| 보고서 작성 | `/pdca report {feature}` |

---

## 핵심 원칙

1. **문서 우선 (Docs First)**: 설계 문서 작성 후 구현
2. **추측 금지 (No Guessing)**: 불확실하면 문서 확인 → 문서에 없으면 질문
3. **설계-구현 동기화**: Gap 분석으로 일관성 유지
