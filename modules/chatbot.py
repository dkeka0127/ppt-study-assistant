"""
AI Tutor Chatbot Module
- Context-aware Q&A based on PPT content via AWS Bedrock
- Conversation memory management
"""

import os
import urllib.parse
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def invoke_bedrock_chat(
    messages: List[Dict],
    system_prompt: str = None,
    max_tokens: int = 2048
) -> str:
    """
    Invoke Bedrock API for chat with Bearer Token authentication.
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
        raise
    except Exception as e:
        print(f"Bedrock API error: {e}")
        raise


def get_tutor_response(
    user_input: str,
    ppt_content: str,
    chat_history: List[Dict[str, str]],
    level: str = "대학생",
    session_id: str = "default"
) -> str:
    """
    Get AI tutor response for user question.

    Args:
        user_input: User's question
        ppt_content: Combined text content from PPT
        chat_history: Previous conversation history
        level: User's learning level
        session_id: Session identifier for history

    Returns:
        AI tutor's response
    """
    # Limit PPT content to avoid token limits
    ppt_content_limited = ppt_content[:8000] if len(ppt_content) > 8000 else ppt_content

    system_prompt = f"""당신은 친절하고 전문적인 AI 학습 튜터입니다. 사용자가 업로드한 PPT 학습 자료를 기반으로 질문에 답변해주세요.

학습자 수준: {level}

PPT 내용:
{ppt_content_limited}

지침:
1. PPT 내용을 기반으로 정확하게 답변하세요.
2. {level} 수준에 맞는 어휘와 설명을 사용하세요.
3. 필요하다면 PPT에 없는 관련 배경 지식도 보충해서 설명하세요.
4. 답변 끝에 관련 슬라이드 번호를 언급해주세요 (예: "이 내용은 슬라이드 3에서 다루고 있습니다").
5. 친근하고 격려하는 톤으로 대화하세요.
6. 사용자가 이해하기 어려워하면 더 쉬운 예시를 들어 설명하세요."""

    try:
        # Build message list for Bedrock
        messages = []

        # Add chat history (last 10 messages for context)
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })

        # Add current user input
        messages.append({
            "role": "user",
            "content": [{"text": user_input}]
        })

        response_text = invoke_bedrock_chat(messages, system_prompt)
        return response_text

    except Exception as e:
        print(f"Error getting tutor response: {e}")
        return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"


def get_suggested_questions(ppt_content: str, level: str = "대학생") -> List[str]:
    """
    Generate suggested questions based on PPT content.

    Args:
        ppt_content: Combined text content from PPT
        level: User's learning level

    Returns:
        List of suggested questions
    """
    try:
        prompt = f"""다음 PPT 내용을 바탕으로 {level} 수준의 학습자가 궁금해할 만한 질문 5개를 생성해주세요.

PPT 내용:
{ppt_content[:2000]}

각 질문은 한 줄로, 번호 없이 작성하세요. 질문만 출력하세요."""

        messages = [{"role": "user", "content": [{"text": prompt}]}]
        response_text = invoke_bedrock_chat(messages, max_tokens=512)

        # Parse questions from response
        questions = [q.strip() for q in response_text.strip().split('\n') if q.strip()]
        return questions[:5]

    except Exception as e:
        print(f"Error generating suggested questions: {e}")
        return [
            "이 주제의 핵심 개념이 뭐야?",
            "시험에 나올만한 중요 문장 3개만 뽑아줘",
            "이 내용을 쉽게 설명해줘",
            "이 주제와 관련된 실생활 예시가 있을까?",
            "이 내용을 요약해줘"
        ]


def format_ppt_for_context(slides_data: List[Dict[str, Any]]) -> str:
    """
    Format slides data into a string for chatbot context.

    Args:
        slides_data: List of slide content data

    Returns:
        Formatted string with all PPT content
    """
    content_parts = []

    for slide in slides_data:
        slide_num = slide.get("slide_num", "?")
        texts = slide.get("texts", [])
        tables = slide.get("tables", [])
        vision_analysis = slide.get("vision_analysis", "")

        parts = [f"[슬라이드 {slide_num}]"]

        if texts:
            parts.append("\n".join(texts))

        if tables:
            for table in tables:
                table_text = "\n".join([" | ".join(row) for row in table])
                parts.append(f"[표]\n{table_text}")

        if vision_analysis:
            parts.append(f"[이미지 분석]\n{vision_analysis}")

        content_parts.append("\n".join(parts))

    return "\n\n".join(content_parts)


def clear_chat_history(session_id: str = "default") -> None:
    """Clear chat history for a session (placeholder for future implementation)."""
    pass
