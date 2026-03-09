"""
AI Tutor Chatbot Module with RAG Pipeline Integration
- Context-aware Q&A using RAG (Retrieval Augmented Generation)
- Vector search with re-ranking for better context selection
- Conversation memory management
"""

import os
import urllib.parse
import requests
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from modules.rag_manager import RAGManager
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGChatbot:
    """Chatbot with RAG pipeline integration."""

    def __init__(
        self,
        collection_name: str = "ppt_study_assistant",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        use_cache: bool = True
    ):
        """
        Initialize RAG-enabled chatbot.

        Args:
            collection_name: Name of the vector database collection
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
            use_cache: Whether to use embedding cache
        """
        self.rag_manager = RAGManager(
            collection_name=collection_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_cache=use_cache
        )

        # Store configuration
        self.collection_name = collection_name
        self.is_initialized = False

        logger.info(f"RAG Chatbot initialized with collection: {collection_name}")

    def initialize_with_ppt(self, slides_data: List[Dict[str, Any]]) -> bool:
        """
        Initialize RAG pipeline with PPT content.

        Args:
            slides_data: List of slide content dictionaries

        Returns:
            Success status
        """
        try:
            # Clear existing collection
            self.rag_manager.clear_collection()

            # Process and index PPT content
            result = self.rag_manager.process_document(
                slides_data,
                merge_small_chunks=False
            )

            self.is_initialized = True
            logger.info(f"RAG pipeline initialized: {result}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            return False

    def get_rag_context(
        self,
        query: str,
        max_tokens: int = 3000,
        top_k_retrieve: int = 10,
        top_n_rerank: int = 5,
        use_diversity: bool = True
    ) -> Tuple[str, List[Dict]]:
        """
        Get optimized context using RAG pipeline.

        Args:
            query: User's question
            max_tokens: Maximum tokens in context
            top_k_retrieve: Number of documents to retrieve
            top_n_rerank: Number of documents after re-ranking
            use_diversity: Whether to use diversity re-ranking

        Returns:
            Tuple of (context_string, source_documents)
        """
        if not self.is_initialized:
            logger.warning("RAG pipeline not initialized, returning empty context")
            return "", []

        return self.rag_manager.get_context(
            query=query,
            max_tokens=max_tokens,
            top_k_retrieve=top_k_retrieve,
            top_n_rerank=top_n_rerank,
            use_diversity=use_diversity
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics."""
        return self.rag_manager.get_statistics()


# Global RAG chatbot instance
_rag_chatbot: Optional[RAGChatbot] = None


def initialize_rag_chatbot(
    slides_data: List[Dict[str, Any]],
    collection_name: str = "ppt_study_assistant",
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> bool:
    """
    Initialize global RAG chatbot with PPT content.

    Args:
        slides_data: List of slide content
        collection_name: Vector DB collection name
        chunk_size: Chunk size for text splitting
        chunk_overlap: Overlap between chunks

    Returns:
        Success status
    """
    global _rag_chatbot

    try:
        # Create RAG chatbot instance
        _rag_chatbot = RAGChatbot(
            collection_name=collection_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_cache=True
        )

        # Initialize with PPT content
        success = _rag_chatbot.initialize_with_ppt(slides_data)

        if success:
            stats = _rag_chatbot.get_statistics()
            logger.info(f"RAG initialization complete. Stats: {stats}")

        return success

    except Exception as e:
        logger.error(f"Failed to initialize RAG chatbot: {e}")
        return False


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
        logger.error(f"Bedrock API request error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        raise
    except KeyError as e:
        logger.error(f"Bedrock API response parsing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Bedrock API error: {e}")
        raise


def get_tutor_response_rag(
    user_input: str,
    chat_history: List[Dict[str, str]],
    level: str = "대학생",
    use_rag: bool = True,
    fallback_context: str = "",
    session_id: str = "default"
) -> Tuple[str, List[Dict]]:
    """
    Get AI tutor response using RAG pipeline.

    Args:
        user_input: User's question
        chat_history: Previous conversation history
        level: User's learning level
        use_rag: Whether to use RAG pipeline
        fallback_context: Fallback context if RAG is not available
        session_id: Session identifier

    Returns:
        Tuple of (response, source_documents)
    """
    global _rag_chatbot

    # Get context using RAG if available
    context = ""
    sources = []

    if use_rag and _rag_chatbot and _rag_chatbot.is_initialized:
        try:
            # Get RAG context with higher quality settings
            context, sources = _rag_chatbot.get_rag_context(
                query=user_input,
                max_tokens=4000,  # Increased for better context
                top_k_retrieve=15,  # Retrieve more candidates
                top_n_rerank=5,  # Keep top 5 after re-ranking
                use_diversity=True  # Ensure diverse perspectives
            )

            if context:
                logger.info(f"RAG context retrieved: {len(context)} chars, {len(sources)} sources")
            else:
                logger.warning("RAG returned empty context, using fallback")
                context = fallback_context[:8000] if fallback_context else ""

        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}, using fallback")
            context = fallback_context[:8000] if fallback_context else ""
    else:
        # Use fallback context if RAG is not available
        context = fallback_context[:8000] if fallback_context else ""
        logger.info(f"Using fallback context: {len(context)} chars")

    # Build system prompt with RAG context
    system_prompt = f"""당신은 친절하고 전문적인 AI 학습 튜터입니다. 사용자가 업로드한 PPT 학습 자료를 기반으로 질문에 답변해주세요.

학습자 수준: {level}

관련 PPT 내용:
{context}

지침:
1. 제공된 PPT 내용을 기반으로 정확하게 답변하세요.
2. {level} 수준에 맞는 어휘와 설명을 사용하세요.
3. 필요하다면 PPT에 없는 관련 배경 지식도 보충해서 설명하세요.
4. 답변에 사용한 정보의 출처(슬라이드 번호)를 명시하세요.
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

        # Sources are still returned for internal use but not shown in response
        return response_text, sources

    except Exception as e:
        logger.error(f"Error getting tutor response: {e}")
        error_msg = f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
        return error_msg, []


def get_suggested_questions_rag(
    user_query: str = None,
    level: str = "대학생",
    fallback_context: str = ""
) -> List[str]:
    """
    Generate suggested questions using RAG context.

    Args:
        user_query: Optional user query for context-aware suggestions
        level: User's learning level
        fallback_context: Fallback context if RAG is not available

    Returns:
        List of suggested questions
    """
    global _rag_chatbot

    try:
        # Get diverse context for generating questions
        context = ""
        if _rag_chatbot and _rag_chatbot.is_initialized:
            # Use a broad query to get diverse content
            broad_query = user_query or "주요 개념 핵심 내용 중요 포인트"
            context, _ = _rag_chatbot.get_rag_context(
                query=broad_query,
                max_tokens=2000,
                top_k_retrieve=10,
                top_n_rerank=5,
                use_diversity=True
            )

        if not context:
            context = fallback_context[:2000] if fallback_context else ""

        prompt = f"""다음 PPT 내용을 바탕으로 {level} 수준의 학습자가 궁금해할 만한 질문 5개를 생성해주세요.

PPT 내용:
{context}

각 질문은 한 줄로, 번호 없이 작성하세요. 질문만 출력하세요."""

        messages = [{"role": "user", "content": [{"text": prompt}]}]
        response_text = invoke_bedrock_chat(messages, max_tokens=512)

        # Parse questions from response
        questions = [q.strip() for q in response_text.strip().split('\n') if q.strip()]
        return questions[:5]

    except Exception as e:
        logger.error(f"Error generating suggested questions: {e}")
        return [
            "이 주제의 핵심 개념이 뭐야?",
            "시험에 나올만한 중요 문장 3개만 뽑아줘",
            "이 내용을 쉽게 설명해줘",
            "이 주제와 관련된 실생활 예시가 있을까?",
            "이 내용을 요약해줘"
        ]


def get_rag_statistics() -> Dict[str, Any]:
    """Get RAG pipeline statistics."""
    global _rag_chatbot

    if _rag_chatbot:
        return _rag_chatbot.get_statistics()
    return {
        "status": "not_initialized",
        "message": "RAG pipeline not initialized"
    }


# Backward compatibility functions
def get_tutor_response(
    user_input: str,
    ppt_content: str,
    chat_history: List[Dict[str, str]],
    level: str = "대학생",
    session_id: str = "default"
) -> str:
    """
    Legacy function for backward compatibility.
    Uses RAG if initialized, otherwise falls back to simple context.
    """
    response, _ = get_tutor_response_rag(
        user_input=user_input,
        chat_history=chat_history,
        level=level,
        use_rag=True,
        fallback_context=ppt_content,
        session_id=session_id
    )
    return response


def get_suggested_questions(ppt_content: str, level: str = "대학생") -> List[str]:
    """
    Legacy function for backward compatibility.
    """
    return get_suggested_questions_rag(
        user_query=None,
        level=level,
        fallback_context=ppt_content
    )


def format_ppt_for_context(slides_data: List[Dict[str, Any]]) -> str:
    """
    Format slides data into a string for chatbot context.
    This is kept for backward compatibility.

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
    """Clear chat history for a session."""
    pass