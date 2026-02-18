"""
Content Generator Module
- Generate summaries using Claude API via AWS Bedrock
- Generate quizzes with various types and difficulty levels
- Analyze images using Claude Vision
"""

import json
import os
import base64
import urllib.parse
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


def clean_json_response(response_text: str) -> str:
    """
    Clean JSON response by removing markdown code blocks and extra text.
    """
    text = response_text.strip()

    # Remove markdown code blocks
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    # Find JSON object boundaries
    text = text.strip()

    # Try to find the start of JSON object or array
    start_idx = -1
    for i, char in enumerate(text):
        if char in '{[':
            start_idx = i
            break

    if start_idx == -1:
        return text

    # Find matching end bracket
    bracket_count = 0
    end_idx = len(text)
    start_char = text[start_idx]
    end_char = '}' if start_char == '{' else ']'

    for i in range(start_idx, len(text)):
        if text[i] == start_char:
            bracket_count += 1
        elif text[i] == end_char:
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = i + 1
                break

    return text[start_idx:end_idx]


def invoke_bedrock_direct(messages: List[Dict], system_prompt: str = None, max_tokens: int = 4096) -> str:
    """
    Directly invoke Bedrock API with Bearer Token authentication.
    """
    region = os.getenv("AWS_REGION", "us-west-2")
    model_id = os.getenv(
        "ANTHROPIC_MODEL",
        "arn:aws:bedrock:us-west-2:850995580124:application-inference-profile/v5nl2gv566vz"
    )
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

    # URL encode the model ID
    encoded_model_id = urllib.parse.quote(model_id, safe='')
    endpoint = f"https://bedrock-runtime.{region}.amazonaws.com/model/{encoded_model_id}/converse"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    body = {
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": 0.7
        }
    }

    if system_prompt:
        body["system"] = [{"text": system_prompt}]

    try:
        response = requests.post(endpoint, json=body, headers=headers, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result["output"]["message"]["content"][0]["text"]
    except requests.exceptions.RequestException as e:
        print(f"Bedrock API request error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        raise
    except KeyError as e:
        print(f"Bedrock API response parsing error: {e}")
        print(f"Full response: {response.text if 'response' in dir() else 'No response'}")
        raise
    except Exception as e:
        print(f"Bedrock API error: {e}")
        raise


def generate_summary(
    slides_data: List[Dict[str, Any]],
    level: str = "대학생"
) -> Dict[str, Any]:
    """
    Generate comprehensive summary of PPT content.

    Args:
        slides_data: List of slide content data
        level: Difficulty level (중학생/고등학생/대학생/전문가)

    Returns:
        Summary dict with one_line, keywords, and slide_summaries
    """
    # Combine all text content
    all_text = []
    for slide in slides_data:
        texts = slide.get("texts", [])
        if texts:
            all_text.append(f"[슬라이드 {slide['slide_num']}]\n" + "\n".join(texts))

    combined_text = "\n\n".join(all_text)

    # Limit text length to avoid token limits
    if len(combined_text) > 15000:
        combined_text = combined_text[:15000] + "\n\n... (내용 생략)"

    system_prompt = f"""당신은 교육 콘텐츠 전문가입니다. 주어진 PPT 내용을 {level} 수준에 맞게 분석하고 요약해주세요.

다음 JSON 형식으로 응답해주세요:
{{
    "one_line": "전체 내용을 한 줄로 요약",
    "keywords": ["핵심키워드1", "핵심키워드2", "핵심키워드3", "핵심키워드4", "핵심키워드5"],
    "slide_summaries": [
        {{
            "slide_num": 1,
            "title": "슬라이드 제목 또는 주제",
            "key_points": ["핵심 포인트 1", "핵심 포인트 2"]
        }}
    ]
}}

반드시 유효한 JSON만 출력하세요. 다른 텍스트는 포함하지 마세요."""

    human_prompt = f"다음 PPT 내용을 분석해주세요:\n\n{combined_text}"

    try:
        messages = [{"role": "user", "content": [{"text": human_prompt}]}]
        response_text = invoke_bedrock_direct(messages, system_prompt)

        # Clean and parse JSON response
        cleaned_json = clean_json_response(response_text)
        result = json.loads(cleaned_json)
        return result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:500] if 'response_text' in dir() else 'No response'}")
        return {
            "one_line": "요약 생성 중 JSON 파싱 오류가 발생했습니다.",
            "keywords": [],
            "slide_summaries": []
        }
    except Exception as e:
        print(f"Error generating summary: {e}")
        return {
            "one_line": f"요약 생성 실패: {str(e)}",
            "keywords": [],
            "slide_summaries": []
        }


def analyze_image(
    image_data: Dict[str, Any],
    slide_context: str = ""
) -> str:
    """
    Analyze an image using Claude Vision API via Bedrock.

    Args:
        image_data: Dict with base64 image and metadata
        slide_context: Text context from the slide

    Returns:
        Analysis text describing the image
    """
    region = os.getenv("AWS_REGION", "us-west-2")
    model_id = os.getenv(
        "ANTHROPIC_MODEL",
        "arn:aws:bedrock:us-west-2:850995580124:application-inference-profile/v5nl2gv566vz"
    )
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

    # URL encode the model ID
    encoded_model_id = urllib.parse.quote(model_id, safe='')
    endpoint = f"https://bedrock-runtime.{region}.amazonaws.com/model/{encoded_model_id}/converse"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    # Build content with image
    content = []

    if slide_context:
        content.append({
            "text": f"이 슬라이드의 텍스트 내용: {slide_context}\n\n위 맥락을 참고하여 아래 이미지를 분석해주세요."
        })

    # Add image - Bedrock expects base64 decoded bytes
    media_type = image_data.get("media_type", "image/png")
    format_type = media_type.split("/")[-1]
    if format_type == "jpg":
        format_type = "jpeg"

    # Decode base64 string to bytes for Bedrock
    image_bytes = base64.b64decode(image_data["base64"])

    content.append({
        "image": {
            "format": format_type,
            "source": {
                "bytes": base64.b64encode(image_bytes).decode('utf-8')
            }
        }
    })

    content.append({
        "text": "이 이미지가 무엇을 나타내는지 학습에 도움이 되도록 설명해주세요. 그래프나 차트인 경우 수치와 트렌드를 해석해주세요."
    })

    body = {
        "messages": [{"role": "user", "content": content}],
        "inferenceConfig": {
            "maxTokens": 1024,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(endpoint, json=body, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["output"]["message"]["content"][0]["text"]
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return f"이미지 분석 실패: {str(e)}"


def generate_quizzes(
    slides_data: List[Dict[str, Any]],
    level: str = "대학생",
    num_questions: int = 10,
    include_types: Dict[str, bool] = None
) -> List[Dict[str, Any]]:
    """
    Generate quizzes based on PPT content.

    Args:
        slides_data: List of slide content data
        level: Difficulty level
        num_questions: Total number of questions
        include_types: Dict of question types to include

    Returns:
        List of quiz stages with questions
    """
    if include_types is None:
        include_types = {
            "multiple_choice": True,
            "short_answer": True,
            "fill_blank": True,
            "essay": False
        }

    # Combine all text content
    all_text = []
    for slide in slides_data:
        texts = slide.get("texts", [])
        if texts:
            all_text.append(f"[슬라이드 {slide['slide_num']}]\n" + "\n".join(texts))

    combined_text = "\n\n".join(all_text)

    # Limit text length
    if len(combined_text) > 12000:
        combined_text = combined_text[:12000] + "\n\n... (내용 생략)"

    # Determine question distribution
    questions_per_stage = max(num_questions // 3, 2)

    type_instructions = []
    if include_types.get("multiple_choice"):
        type_instructions.append("- multiple_choice: 4지선다 객관식")
    if include_types.get("short_answer"):
        type_instructions.append("- short_answer: 단답형 (1-3단어)")
    if include_types.get("fill_blank"):
        type_instructions.append("- fill_blank: 빈칸 채우기")
    if include_types.get("essay"):
        type_instructions.append("- essay: 서술형")

    system_prompt = f"""당신은 교육 평가 전문가입니다. 주어진 PPT 내용을 바탕으로 {level} 수준에 맞는 퀴즈를 생성해주세요.

문제 유형:
{chr(10).join(type_instructions)}

다음 JSON 형식으로 응답해주세요:
{{
    "stages": [
        {{
            "stage": "기초다지기",
            "questions": [
                {{
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "문제 내용",
                    "options": ["보기1", "보기2", "보기3", "보기4"],
                    "answer": 0,
                    "source_slide": 1,
                    "explanation": "해설"
                }}
            ]
        }},
        {{
            "stage": "실력다지기",
            "questions": [...]
        }},
        {{
            "stage": "심화학습",
            "questions": [...]
        }}
    ]
}}

규칙:
1. 각 단계별로 {questions_per_stage}개 이상의 문제를 생성하세요.
2. "기초다지기"는 용어와 정의 중심, "실력다지기"는 개념 적용, "심화학습"은 종합적 사고력 문제입니다.
3. 각 문제의 source_slide는 해당 내용이 나온 실제 슬라이드 번호를 정확히 기재하세요.
4. multiple_choice의 answer는 정답 보기의 인덱스(0부터 시작)입니다.
5. 반드시 유효한 JSON만 출력하세요. 다른 텍스트는 절대 포함하지 마세요."""

    human_prompt = f"다음 PPT 내용을 바탕으로 총 {num_questions}개의 퀴즈를 생성해주세요:\n\n{combined_text}"

    try:
        messages = [{"role": "user", "content": [{"text": human_prompt}]}]
        response_text = invoke_bedrock_direct(messages, system_prompt, max_tokens=8000)

        # Clean and parse JSON response
        cleaned_json = clean_json_response(response_text)
        result = json.loads(cleaned_json)

        # Assign sequential IDs
        question_id = 1
        for stage in result.get("stages", []):
            for question in stage.get("questions", []):
                question["id"] = question_id
                question_id += 1

        return result.get("stages", [])

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:1000] if 'response_text' in dir() else 'No response'}")
        return get_fallback_quizzes()
    except Exception as e:
        print(f"Error generating quizzes: {e}")
        return get_fallback_quizzes()


def get_fallback_quizzes() -> List[Dict[str, Any]]:
    """Return fallback quizzes when generation fails."""
    return [
        {
            "stage": "기초다지기",
            "questions": [{
                "id": 1,
                "type": "multiple_choice",
                "question": "퀴즈 생성 중 오류가 발생했습니다. 다시 시도해주세요.",
                "options": ["옵션 1", "옵션 2", "옵션 3", "옵션 4"],
                "answer": 0,
                "source_slide": 1,
                "explanation": "퀴즈 생성 실패"
            }]
        },
        {"stage": "실력다지기", "questions": []},
        {"stage": "심화학습", "questions": []}
    ]


def generate_feedback(
    wrong_answers: List[Dict[str, Any]],
    slides_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate personalized feedback based on wrong answers.

    Args:
        wrong_answers: List of incorrectly answered questions
        slides_data: Original slide data for context

    Returns:
        Feedback dict with analysis and recommendations
    """
    if not wrong_answers:
        return {
            "analysis": "모든 문제를 맞추셨습니다! 훌륭합니다.",
            "weak_areas": [],
            "recommendations": []
        }

    # Prepare wrong answer summary
    wrong_summary = []
    for wa in wrong_answers:
        q = wa["question"]
        wrong_summary.append(f"""
문제: {q['question']}
사용자 답변: {wa['user_answer']}
정답: {wa['correct_answer']}
출처: 슬라이드 {q.get('source_slide', '?')}
""")

    system_prompt = """당신은 학습 코치입니다. 사용자의 오답을 분석하고 개인화된 피드백을 제공해주세요.

다음 JSON 형식으로 응답해주세요:
{
    "analysis": "전반적인 분석 (2-3문장)",
    "weak_areas": [
        {
            "area": "취약 영역명",
            "description": "설명",
            "related_slides": [1, 2]
        }
    ],
    "recommendations": ["추천 학습 방법 1", "추천 학습 방법 2"]
}

반드시 유효한 JSON만 출력하세요."""

    human_prompt = f"다음 오답들을 분석해주세요:\n\n{''.join(wrong_summary)}"

    try:
        messages = [{"role": "user", "content": [{"text": human_prompt}]}]
        response_text = invoke_bedrock_direct(messages, system_prompt, max_tokens=2000)

        # Clean and parse JSON response
        cleaned_json = clean_json_response(response_text)
        return json.loads(cleaned_json)

    except Exception as e:
        print(f"Error generating feedback: {e}")
        return {
            "analysis": "피드백 생성 중 오류가 발생했습니다.",
            "weak_areas": [],
            "recommendations": ["오답 노트를 복습하세요.", "해당 슬라이드를 다시 확인하세요."]
        }
