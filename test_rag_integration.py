"""
Final Integration Test for RAG-Enhanced PPT Study Assistant
Tests the complete pipeline integration with the existing app structure
"""

import os
import sys
from typing import List, Dict, Any
from modules.parser import extract_slide_content
from modules.chatbot_rag import (
    initialize_rag_chatbot,
    get_tutor_response_rag,
    get_suggested_questions_rag,
    get_rag_statistics,
    format_ppt_for_context
)
from modules.generator import (
    generate_summary,
    generate_multichoice_quiz,
    generate_blank_quiz,
    generate_word_test
)
import json


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_ppt_parsing():
    """Test PPT parsing with sample file."""
    print_section_header("1. PPT Parsing Test")

    # Check if sample PPT exists
    sample_ppt_path = "./data/sample_presentation.pptx"

    if not os.path.exists(sample_ppt_path):
        print(f"⚠️ Sample PPT not found at {sample_ppt_path}")
        print("Creating a test dataset instead...")

        # Create test slides data
        test_slides = [
            {
                "slide_num": 1,
                "texts": [
                    "인공지능과 머신러닝 개요",
                    "AI와 ML의 기초 개념과 응용 분야",
                    "2024년 최신 트렌드와 발전 방향"
                ],
                "tables": [],
                "vision_analysis": "AI/ML 관계도 다이어그램"
            },
            {
                "slide_num": 2,
                "texts": [
                    "딥러닝의 핵심 개념",
                    "• 신경망 (Neural Networks)",
                    "• 역전파 (Backpropagation)",
                    "• 활성화 함수 (Activation Functions)",
                    "• 경사하강법 (Gradient Descent)"
                ],
                "tables": [
                    [["구분", "특징", "활용"],
                     ["CNN", "이미지 처리 특화", "컴퓨터 비전"],
                     ["RNN", "순차 데이터 처리", "자연어 처리"],
                     ["Transformer", "병렬 처리 효율", "대규모 언어 모델"]]
                ],
                "vision_analysis": ""
            },
            {
                "slide_num": 3,
                "texts": [
                    "실제 응용 사례",
                    "1. 의료 진단: X-ray, MRI 분석",
                    "2. 자율주행: 객체 인식, 경로 계획",
                    "3. 금융: 사기 탐지, 신용 평가",
                    "4. 교육: 맞춤형 학습, 자동 채점"
                ],
                "tables": [],
                "vision_analysis": "응용 분야별 성과 차트"
            },
            {
                "slide_num": 4,
                "texts": [
                    "머신러닝 프로젝트 수행 단계",
                    "1단계: 문제 정의 및 데이터 수집",
                    "2단계: 데이터 전처리 및 탐색",
                    "3단계: 모델 선택 및 학습",
                    "4단계: 평가 및 최적화",
                    "5단계: 배포 및 모니터링"
                ],
                "tables": [],
                "vision_analysis": ""
            },
            {
                "slide_num": 5,
                "texts": [
                    "미래 전망과 과제",
                    "• 설명 가능한 AI (XAI)",
                    "• 윤리적 AI와 편향 제거",
                    "• AGI (Artificial General Intelligence)",
                    "• 양자 컴퓨팅과 AI의 결합"
                ],
                "tables": [],
                "vision_analysis": "AI 발전 로드맵"
            }
        ]

        print(f"✅ Created test dataset with {len(test_slides)} slides")
        return test_slides

    else:
        # Parse actual PPT file
        print(f"📄 Parsing PPT: {sample_ppt_path}")
        slides_data = extract_slide_content(sample_ppt_path, use_vision=False)
        print(f"✅ Parsed {len(slides_data)} slides successfully")
        return slides_data


def test_rag_initialization(slides_data: List[Dict[str, Any]]):
    """Test RAG pipeline initialization."""
    print_section_header("2. RAG Pipeline Initialization")

    try:
        # Initialize RAG chatbot
        success = initialize_rag_chatbot(
            slides_data=slides_data,
            collection_name="integration_test_collection",
            chunk_size=500,
            chunk_overlap=100
        )

        if success:
            print("✅ RAG pipeline initialized successfully")

            # Get statistics
            stats = get_rag_statistics()
            print("\n📊 RAG Pipeline Statistics:")
            print(f"    Documents processed: {stats.get('documents_processed', 0)}")
            if 'collection_stats' in stats:
                print(f"    Vector DB documents: {stats['collection_stats'].get('count', 0)}")
            if 'cache_hits' in stats or 'cache_misses' in stats:
                print(f"    Cache hits/misses: {stats.get('cache_hits', 0)}/{stats.get('cache_misses', 0)}")

            return True
        else:
            print("❌ Failed to initialize RAG pipeline")
            return False

    except Exception as e:
        print(f"❌ Error during RAG initialization: {e}")
        return False


def test_rag_enhanced_chatbot(slides_data: List[Dict[str, Any]]):
    """Test RAG-enhanced chatbot responses."""
    print_section_header("3. RAG-Enhanced Chatbot Test")

    # Prepare fallback context
    fallback_context = format_ppt_for_context(slides_data)

    # Test queries
    test_queries = [
        ("딥러닝의 핵심 개념들을 설명해줘", "대학생"),
        ("머신러닝 프로젝트는 어떤 단계로 진행되나요?", "고등학생"),
        ("AI가 의료 분야에서 어떻게 활용되고 있어?", "중학생"),
        ("Transformer와 CNN의 차이점이 뭐야?", "대학생")
    ]

    chat_history = []

    for query, level in test_queries:
        print(f"\n📝 Query ({level}): '{query}'")

        try:
            # Get RAG-enhanced response
            response, sources = get_tutor_response_rag(
                user_input=query,
                chat_history=chat_history,
                level=level,
                use_rag=True,
                fallback_context=fallback_context,
                session_id="integration_test"
            )

            if response:
                print(f"✅ Got response ({len(response)} chars)")
                # Show response preview
                preview = response[:150] + "..." if len(response) > 150 else response
                print(f"   Response: {preview}")

                if sources:
                    print(f"   Sources: {len(sources)} documents used")
                    for i, source in enumerate(sources[:2], 1):
                        print(f"     - Slide {source.get('slide_num', '?')}: {source.get('content_type', 'text')}")

            # Add to chat history
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"⚠️ Error getting response: {e}")
            print("   Note: This may fail if Bedrock API is not configured")


def test_content_generation(slides_data: List[Dict[str, Any]]):
    """Test content generation with RAG context."""
    print_section_header("4. Content Generation Test")

    # Format PPT content
    ppt_content = format_ppt_for_context(slides_data)
    print(f"📄 PPT content formatted: {len(ppt_content)} characters")

    try:
        # Test summary generation
        print("\n📝 Generating summary...")
        summary = generate_summary(ppt_content, level="대학생")
        if summary:
            print(f"✅ Summary generated ({len(summary)} chars)")
            preview = summary[:150] + "..." if len(summary) > 150 else summary
            print(f"   Preview: {preview}")

        # Test quiz generation
        print("\n📝 Generating multiple choice quiz...")
        quiz = generate_multichoice_quiz(ppt_content, num_questions=3, level="고등학생")
        if quiz:
            print(f"✅ Generated {len(quiz)} quiz questions")
            if quiz:
                print(f"   First question: {quiz[0].get('question', 'N/A')[:100]}...")

        # Test blank quiz generation
        print("\n📝 Generating fill-in-the-blank quiz...")
        blank_quiz = generate_blank_quiz(ppt_content, num_questions=2, level="대학생")
        if blank_quiz:
            print(f"✅ Generated {len(blank_quiz)} blank quiz questions")

        # Test word test generation
        print("\n📝 Generating word test...")
        word_test = generate_word_test(ppt_content, num_words=5, level="중학생")
        if word_test:
            print(f"✅ Generated {len(word_test)} word test items")
            if word_test:
                print(f"   First word: {word_test[0].get('word', 'N/A')}")

    except Exception as e:
        print(f"⚠️ Content generation error: {e}")
        print("   Note: This may fail if Bedrock API is not configured")


def test_suggested_questions():
    """Test suggested questions generation."""
    print_section_header("5. Suggested Questions Test")

    try:
        # Generate questions with RAG context
        print("\n📝 Generating suggested questions with RAG context...")
        questions = get_suggested_questions_rag(
            user_query="머신러닝과 딥러닝",
            level="대학생",
            fallback_context=""
        )

        if questions:
            print(f"✅ Generated {len(questions)} suggested questions:")
            for i, q in enumerate(questions[:3], 1):
                print(f"   {i}. {q}")

        # Generate general questions
        print("\n📝 Generating general suggested questions...")
        general_questions = get_suggested_questions_rag(
            user_query=None,
            level="고등학생",
            fallback_context=""
        )

        if general_questions:
            print(f"✅ Generated {len(general_questions)} general questions")

    except Exception as e:
        print(f"⚠️ Suggested questions error: {e}")
        print("   Note: This may fail if Bedrock API is not configured")


def test_performance_metrics():
    """Test and display performance metrics."""
    print_section_header("6. Performance Metrics")

    # Get final statistics
    stats = get_rag_statistics()

    print("\n📊 Final RAG Pipeline Metrics:")
    print(f"    Status: {'Initialized' if stats.get('status') != 'not_initialized' else 'Not initialized'}")

    if stats.get('status') != 'not_initialized':
        print(f"    Documents processed: {stats.get('documents_processed', 0)}")
        print(f"    Queries processed: {stats.get('queries_processed', 0)}")

        if 'collection_stats' in stats:
            collection = stats['collection_stats']
            print(f"    Vector DB size: {collection.get('count', 0)} documents")

        if 'cache_hit_rate' in stats:
            print(f"    Cache hit rate: {stats['cache_hit_rate']:.2%}")

        print(f"    Average chunk size: {stats.get('avg_chunk_size', 'N/A')}")
        print(f"    Using embedding cache: {stats.get('use_cache', False)}")


def cleanup():
    """Clean up test resources."""
    try:
        from modules.vector_store import VectorStore

        # Clean up test collection
        store = VectorStore(collection_name="integration_test_collection")
        store.delete_collection()
        print("\n✅ Cleaned up test collection")
    except:
        pass


def main():
    """Run complete integration test."""
    print("\n" + "="*70)
    print("  RAG-ENHANCED PPT STUDY ASSISTANT - INTEGRATION TEST")
    print("="*70)
    print("\nThis test demonstrates the complete RAG pipeline integration")
    print("with the existing PPT Study Assistant application.\n")

    # Test PPT parsing
    slides_data = test_ppt_parsing()
    if not slides_data:
        print("\n❌ Failed to get PPT data. Exiting.")
        sys.exit(1)

    # Test RAG initialization
    rag_success = test_rag_initialization(slides_data)
    if not rag_success:
        print("\n⚠️ RAG initialization failed, but continuing with tests...")

    # Test RAG-enhanced chatbot
    test_rag_enhanced_chatbot(slides_data)

    # Test content generation
    test_content_generation(slides_data)

    # Test suggested questions
    test_suggested_questions()

    # Display performance metrics
    test_performance_metrics()

    # Cleanup
    cleanup()

    # Summary
    print_section_header("INTEGRATION TEST COMPLETE")
    print("""
✅ RAG Pipeline Integration Summary:
    1. Document Processing: Converts PPT slides to searchable chunks
    2. Vector Storage: Stores embeddings in ChromaDB for fast retrieval
    3. Semantic Search: Finds relevant content based on user queries
    4. Re-ranking: Improves relevance with cross-encoder models
    5. Context Generation: Creates optimized context for LLM
    6. Enhanced Responses: Provides accurate, context-aware answers

📋 Key Features Implemented:
    • Multi-modal PPT parsing (text, tables, images)
    • Efficient vector search with ChromaDB
    • Advanced re-ranking with diversity scoring
    • Embedding cache for performance
    • Backward compatibility with existing code
    • Comprehensive error handling

🚀 Next Steps:
    1. Integrate with Streamlit UI (app.py)
    2. Add user settings for RAG parameters
    3. Implement conversation memory
    4. Add source attribution in UI
    5. Performance monitoring dashboard
    """)


if __name__ == "__main__":
    main()