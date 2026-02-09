"""
AI Tutor Chatbot Module
- Context-aware Q&A based on PPT content
- Conversation memory management
- LangChain integration for chat functionality
"""

import os
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv

load_dotenv()


class InMemoryChatHistory(BaseChatMessageHistory):
    """Simple in-memory chat history storage."""

    def __init__(self):
        self.messages: List = []

    def add_message(self, message) -> None:
        self.messages.append(message)

    def add_messages(self, messages: List) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


# Global storage for chat histories
chat_histories: Dict[str, InMemoryChatHistory] = {}


def get_chat_history(session_id: str) -> InMemoryChatHistory:
    """Get or create chat history for a session."""
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatHistory()
    return chat_histories[session_id]


def create_tutor_chain(ppt_content: str, level: str = "대학생"):
    """
    Create a chat chain with PPT context.

    Args:
        ppt_content: Combined text content from PPT
        level: User's learning level

    Returns:
        Configured chat chain
    """
    model = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2048
    )

    system_template = f"""당신은 친절하고 전문적인 AI 학습 튜터입니다. 사용자가 업로드한 PPT 학습 자료를 기반으로 질문에 답변해주세요.

학습자 수준: {level}

PPT 내용:
{ppt_content}

지침:
1. PPT 내용을 기반으로 정확하게 답변하세요.
2. {level} 수준에 맞는 어휘와 설명을 사용하세요.
3. 필요하다면 PPT에 없는 관련 배경 지식도 보충해서 설명하세요.
4. 답변 끝에 관련 슬라이드 번호를 언급해주세요 (예: "이 내용은 슬라이드 3에서 다루고 있습니다").
5. 친근하고 격려하는 톤으로 대화하세요.
6. 사용자가 이해하기 어려워하면 더 쉬운 예시를 들어 설명하세요."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | model

    return RunnableWithMessageHistory(
        chain,
        get_chat_history,
        input_messages_key="input",
        history_messages_key="history"
    )


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
    try:
        model = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=2048
        )

        system_prompt = f"""당신은 친절하고 전문적인 AI 학습 튜터입니다. 사용자가 업로드한 PPT 학습 자료를 기반으로 질문에 답변해주세요.

학습자 수준: {level}

PPT 내용:
{ppt_content}

지침:
1. PPT 내용을 기반으로 정확하게 답변하세요.
2. {level} 수준에 맞는 어휘와 설명을 사용하세요.
3. 필요하다면 PPT에 없는 관련 배경 지식도 보충해서 설명하세요.
4. 답변 끝에 관련 슬라이드 번호를 언급해주세요 (예: "이 내용은 슬라이드 3에서 다루고 있습니다").
5. 친근하고 격려하는 톤으로 대화하세요.
6. 사용자가 이해하기 어려워하면 더 쉬운 예시를 들어 설명하세요."""

        # Build message list
        messages = [SystemMessage(content=system_prompt)]

        # Add chat history
        for msg in chat_history[-10:]:  # Keep last 10 messages for context
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current user input
        messages.append(HumanMessage(content=user_input))

        response = model.invoke(messages)
        return response.content

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
        model = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=512
        )

        prompt = f"""다음 PPT 내용을 바탕으로 {level} 수준의 학습자가 궁금해할 만한 질문 5개를 생성해주세요.

PPT 내용:
{ppt_content[:2000]}

각 질문은 한 줄로, 번호 없이 작성하세요. 질문만 출력하세요."""

        response = model.invoke([HumanMessage(content=prompt)])

        # Parse questions from response
        questions = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
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


def clear_chat_history(session_id: str = "default") -> None:
    """Clear chat history for a session."""
    if session_id in chat_histories:
        chat_histories[session_id].clear()


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
