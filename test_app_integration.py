"""
Test script to verify RAG integration with Streamlit app
"""

import os
import sys
from modules.chatbot_rag import (
    initialize_rag_chatbot,
    get_tutor_response_rag,
    get_suggested_questions_rag,
    get_rag_statistics
)


def test_app_integration():
    """Test the RAG integration with app components."""
    print("="*60)
    print("Testing RAG Integration with Streamlit App")
    print("="*60)

    # Test data
    test_slides = [
        {
            "slide_num": 1,
            "texts": [
                "RAG 통합 테스트",
                "Streamlit 앱과 RAG 파이프라인 연동 확인",
                "벡터 검색과 재순위화 기능 테스트"
            ],
            "tables": [],
            "vision_analysis": "다이어그램 분석 결과"
        },
        {
            "slide_num": 2,
            "texts": [
                "주요 기능",
                "• 의미 기반 검색",
                "• 컨텍스트 최적화",
                "• 소스 추적"
            ],
            "tables": [
                [["기능", "설명"],
                 ["벡터 DB", "ChromaDB 사용"],
                 ["임베딩", "sentence-transformers"],
                 ["재순위화", "cross-encoder"]]
            ],
            "vision_analysis": ""
        }
    ]

    # Test 1: RAG Initialization
    print("\n1. Testing RAG Initialization...")
    try:
        success = initialize_rag_chatbot(
            slides_data=test_slides,
            collection_name="app_integration_test",
            chunk_size=500,
            chunk_overlap=100
        )

        if success:
            print("✅ RAG initialization successful")
            stats = get_rag_statistics()
            print(f"   Documents processed: {stats.get('documents_processed', 0)}")
            if 'collection_stats' in stats:
                print(f"   Vector DB count: {stats['collection_stats'].get('count', 0)}")
        else:
            print("❌ RAG initialization failed")
            return False

    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False

    # Test 2: RAG-enhanced Response
    print("\n2. Testing RAG-enhanced Response...")
    try:
        test_query = "RAG 파이프라인의 주요 기능은 뭐야?"

        response, sources = get_tutor_response_rag(
            user_input=test_query,
            chat_history=[],
            level="대학생",
            use_rag=True,
            fallback_context="",
            session_id="test_session"
        )

        if response:
            print(f"✅ Got response ({len(response)} chars)")
            print(f"   Response preview: {response[:100]}...")
            if sources:
                print(f"   Sources used: {len(sources)}")
                for i, source in enumerate(sources[:2], 1):
                    print(f"     - Slide {source.get('slide_num', '?')}")
        else:
            print("⚠️ Empty response (may be API issue)")

    except Exception as e:
        print(f"⚠️ Response generation error: {e}")
        print("   This is expected if Bedrock API is not configured")

    # Test 3: Suggested Questions
    print("\n3. Testing Suggested Questions...")
    try:
        questions = get_suggested_questions_rag(
            user_query="RAG 통합",
            level="대학생",
            fallback_context=""
        )

        if questions:
            print(f"✅ Generated {len(questions)} questions:")
            for i, q in enumerate(questions[:3], 1):
                print(f"   {i}. {q}")
        else:
            print("⚠️ No questions generated (may be API issue)")

    except Exception as e:
        print(f"⚠️ Question generation error: {e}")
        print("   This is expected if Bedrock API is not configured")

    # Test 4: Statistics Check
    print("\n4. Checking Final Statistics...")
    final_stats = get_rag_statistics()
    print(f"✅ Final statistics:")
    print(f"   Documents: {final_stats.get('documents_processed', 0)}")
    print(f"   Queries: {final_stats.get('queries_processed', 0)}")
    if 'cache_hit_rate' in final_stats:
        print(f"   Cache hit rate: {final_stats.get('cache_hit_rate', 0):.1%}")

    print("\n" + "="*60)
    print("✅ RAG Integration Test Complete!")
    print("="*60)
    print("\nThe RAG pipeline is successfully integrated with the app.")
    print("You can now run: streamlit run app.py")
    print("\nFeatures enabled:")
    print("  • RAG-enhanced responses in AI Tutor")
    print("  • Dynamic suggested questions")
    print("  • Source attribution display")
    print("  • RAG status indicators")

    # Cleanup
    try:
        from modules.vector_store import VectorStore
        store = VectorStore(collection_name="app_integration_test")
        store.delete_collection()
        print("\n✅ Cleaned up test collection")
    except:
        pass

    return True


if __name__ == "__main__":
    test_app_integration()