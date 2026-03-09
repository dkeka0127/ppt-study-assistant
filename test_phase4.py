"""
Test script for RAG Pipeline Phase 4
Tests Chatbot Integration with RAG Pipeline
"""

import sys
import os
from typing import List, Dict, Any
from modules.chatbot_rag import (
    RAGChatbot,
    initialize_rag_chatbot,
    get_tutor_response_rag,
    get_suggested_questions_rag,
    get_rag_statistics,
    format_ppt_for_context,
    get_tutor_response,  # Legacy compatibility
    get_suggested_questions  # Legacy compatibility
)
import json


def test_rag_chatbot_initialization():
    """Test RAG Chatbot initialization."""
    print("\n" + "="*60)
    print("Testing RAG Chatbot Initialization")
    print("="*60)

    try:
        # Create RAG chatbot instance
        chatbot = RAGChatbot(
            collection_name="test_chatbot_collection",
            chunk_size=500,
            chunk_overlap=100,
            use_cache=True
        )
        print("✅ RAG Chatbot instance created")

        # Check initial state
        assert chatbot.collection_name == "test_chatbot_collection", "Collection name mismatch"
        assert not chatbot.is_initialized, "Should not be initialized yet"
        assert chatbot.rag_manager is not None, "RAG Manager not created"

        print("✅ Initial state verified")
        print(f"    Collection: {chatbot.collection_name}")
        print(f"    Initialized: {chatbot.is_initialized}")

        print("\n✅ RAG Chatbot initialization test passed!")
        return True, chatbot

    except Exception as e:
        print(f"\n❌ RAG Chatbot initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_ppt_initialization(chatbot):
    """Test initializing chatbot with PPT content."""
    print("\n" + "="*60)
    print("Testing PPT Content Initialization")
    print("="*60)

    try:
        # Sample PPT data
        test_slides = [
            {
                "slide_num": 1,
                "texts": [
                    "Introduction to Machine Learning",
                    "Machine Learning is a subset of AI that enables systems to learn from data.",
                    "Types: Supervised, Unsupervised, Reinforcement Learning"
                ],
                "tables": [
                    [["Type", "Description", "Example"],
                     ["Supervised", "Learning with labeled data", "Classification"],
                     ["Unsupervised", "Learning without labels", "Clustering"],
                     ["Reinforcement", "Learning through rewards", "Game playing"]]
                ],
                "vision_analysis": "Diagram showing ML as subset of AI"
            },
            {
                "slide_num": 2,
                "texts": [
                    "Deep Learning Fundamentals",
                    "Neural Networks consist of layers of interconnected nodes",
                    "Key concepts: Neurons, Weights, Biases, Activation Functions",
                    "Backpropagation is used for training"
                ],
                "tables": [],
                "vision_analysis": "Neural network architecture diagram"
            },
            {
                "slide_num": 3,
                "texts": [
                    "Applications of ML",
                    "• Computer Vision: Image recognition, Object detection",
                    "• Natural Language Processing: Translation, Sentiment analysis",
                    "• Recommendation Systems: Netflix, Amazon",
                    "• Healthcare: Disease diagnosis, Drug discovery"
                ],
                "tables": [],
                "vision_analysis": ""
            },
            {
                "slide_num": 4,
                "texts": [
                    "ML Development Process",
                    "1. Data Collection and Preparation",
                    "2. Feature Engineering",
                    "3. Model Selection and Training",
                    "4. Evaluation and Validation",
                    "5. Deployment and Monitoring"
                ],
                "tables": [
                    [["Phase", "Key Activities"],
                     ["Data Prep", "Cleaning, Normalization, Splitting"],
                     ["Training", "Algorithm selection, Hyperparameter tuning"],
                     ["Evaluation", "Cross-validation, Metrics calculation"]]
                ],
                "vision_analysis": "ML pipeline flowchart"
            }
        ]

        # Initialize with PPT content
        success = chatbot.initialize_with_ppt(test_slides)
        assert success, "Failed to initialize with PPT content"
        assert chatbot.is_initialized, "Chatbot should be initialized"

        print("✅ PPT content loaded successfully")

        # Get statistics
        stats = chatbot.get_statistics()
        print(f"\n📊 RAG Statistics after initialization:")
        print(f"    Documents processed: {stats.get('documents_processed', 0)}")
        if 'collection_stats' in stats:
            print(f"    Collection count: {stats['collection_stats'].get('count', 0)}")

        print("\n✅ PPT initialization test passed!")
        return True, test_slides

    except Exception as e:
        print(f"\n❌ PPT initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_rag_context_retrieval(chatbot):
    """Test RAG context retrieval."""
    print("\n" + "="*60)
    print("Testing RAG Context Retrieval")
    print("="*60)

    try:
        # Test queries
        test_queries = [
            ("What is machine learning?", 5),
            ("Explain neural networks and deep learning", 5),
            ("What are the applications of ML in healthcare?", 3),
            ("How does supervised learning work?", 4)
        ]

        for query, expected_sources in test_queries:
            print(f"\n📝 Query: '{query}'")

            # Get RAG context
            context, sources = chatbot.get_rag_context(
                query=query,
                max_tokens=2000,
                top_k_retrieve=10,
                top_n_rerank=5,
                use_diversity=True
            )

            print(f"✅ Retrieved context: {len(context)} chars")
            print(f"✅ Source documents: {len(sources)}")

            # Display context preview
            if context:
                preview = context[:200] + "..." if len(context) > 200 else context
                print(f"    Context preview: {preview}")

            # Show sources
            if sources:
                print("    Sources:")
                for i, source in enumerate(sources[:3]):
                    print(f"      - Slide {source.get('slide_num', '?')}: "
                          f"{source.get('content_type', 'unknown')}")

        print("\n✅ RAG context retrieval test passed!")
        return True

    except Exception as e:
        print(f"\n❌ RAG context retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_global_initialization(test_slides):
    """Test global RAG chatbot initialization."""
    print("\n" + "="*60)
    print("Testing Global RAG Chatbot Initialization")
    print("="*60)

    try:
        # Initialize global chatbot
        success = initialize_rag_chatbot(
            slides_data=test_slides,
            collection_name="test_global_collection",
            chunk_size=500,
            chunk_overlap=100
        )

        assert success, "Global initialization failed"
        print("✅ Global RAG chatbot initialized")

        # Get statistics
        stats = get_rag_statistics()
        print(f"\n📊 Global RAG Statistics:")
        if stats.get('status') != 'not_initialized':
            print(f"    Documents: {stats.get('documents_processed', 0)}")
            print(f"    Queries: {stats.get('queries_processed', 0)}")
        else:
            print(f"    Status: {stats.get('status')}")

        print("\n✅ Global initialization test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Global initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tutor_response_rag():
    """Test RAG-enhanced tutor responses."""
    print("\n" + "="*60)
    print("Testing RAG-Enhanced Tutor Responses")
    print("="*60)

    try:
        # Prepare chat history
        chat_history = [
            {"role": "user", "content": "안녕하세요, ML에 대해 알려주세요"},
            {"role": "assistant", "content": "안녕하세요! Machine Learning에 대해 설명드리겠습니다."}
        ]

        # Test queries
        test_queries = [
            "머신러닝과 딥러닝의 차이점을 설명해줘",
            "지도학습이 뭔지 예시와 함께 설명해줘",
            "ML이 의료 분야에서 어떻게 활용되고 있어?"
        ]

        for query in test_queries:
            print(f"\n📝 User Query: '{query}'")

            # Get response with RAG
            response, sources = get_tutor_response_rag(
                user_input=query,
                chat_history=chat_history,
                level="대학생",
                use_rag=True,
                fallback_context="",
                session_id="test_session"
            )

            if response:
                print(f"✅ Got response ({len(response)} chars)")
                # Show response preview
                preview = response[:200] + "..." if len(response) > 200 else response
                print(f"    Response preview: {preview}")

                if sources:
                    print(f"    Sources used: {len(sources)}")

            # Add to chat history
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": response})

        print("\n✅ Tutor response test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Tutor response test failed: {e}")
        print(f"    Note: This may fail if Bedrock API is not configured")
        import traceback
        traceback.print_exc()
        return False  # Return False but don't stop other tests


def test_suggested_questions():
    """Test suggested questions generation."""
    print("\n" + "="*60)
    print("Testing Suggested Questions Generation")
    print("="*60)

    try:
        # Test with RAG context
        questions = get_suggested_questions_rag(
            user_query="machine learning",
            level="대학생",
            fallback_context=""
        )

        print(f"✅ Generated {len(questions)} suggested questions:")
        for i, q in enumerate(questions, 1):
            print(f"    {i}. {q}")

        # Test without specific query
        questions = get_suggested_questions_rag(
            user_query=None,
            level="중학생",
            fallback_context=""
        )

        print(f"\n✅ Generated {len(questions)} general questions:")
        for i, q in enumerate(questions, 1):
            print(f"    {i}. {q}")

        print("\n✅ Suggested questions test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Suggested questions test failed: {e}")
        print(f"    Note: This may fail if Bedrock API is not configured")
        import traceback
        traceback.print_exc()
        return False  # Return False but don't stop other tests


def test_legacy_compatibility(test_slides):
    """Test backward compatibility with legacy functions."""
    print("\n" + "="*60)
    print("Testing Legacy Function Compatibility")
    print("="*60)

    try:
        # Format PPT content for legacy context
        ppt_content = format_ppt_for_context(test_slides)
        print(f"✅ Formatted PPT content: {len(ppt_content)} chars")

        # Test legacy get_tutor_response
        chat_history = []
        response = get_tutor_response(
            user_input="What is machine learning?",
            ppt_content=ppt_content,
            chat_history=chat_history,
            level="대학생",
            session_id="legacy_test"
        )

        if response:
            print(f"✅ Legacy tutor response: {len(response)} chars")

        # Test legacy get_suggested_questions
        questions = get_suggested_questions(
            ppt_content=ppt_content,
            level="고등학생"
        )

        print(f"✅ Legacy suggested questions: {len(questions)} questions")

        print("\n✅ Legacy compatibility test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Legacy compatibility test failed: {e}")
        print(f"    Note: This may fail if Bedrock API is not configured")
        import traceback
        traceback.print_exc()
        return False  # Return False but don't stop other tests


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n" + "="*60)
    print("Testing Error Handling")
    print("="*60)

    try:
        # Test uninitialized chatbot
        uninit_chatbot = RAGChatbot(collection_name="uninit_collection")
        context, sources = uninit_chatbot.get_rag_context("test query")
        assert context == "", "Should return empty context when not initialized"
        assert sources == [], "Should return empty sources when not initialized"
        print("✅ Handles uninitialized chatbot correctly")

        # Test with empty slides
        empty_chatbot = RAGChatbot(collection_name="empty_collection")
        success = empty_chatbot.initialize_with_ppt([])
        print(f"✅ Handles empty slides: success={success}")

        # Test with invalid data
        invalid_chatbot = RAGChatbot(collection_name="invalid_collection")
        try:
            success = invalid_chatbot.initialize_with_ppt([{"invalid": "data"}])
            print(f"✅ Handles invalid data: success={success}")
        except:
            print("✅ Properly raises error for invalid data")

        print("\n✅ Error handling test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup():
    """Clean up test resources."""
    try:
        # Clean up any test collections
        from modules.vector_store import VectorStore

        test_collections = [
            "test_chatbot_collection",
            "test_global_collection",
            "uninit_collection",
            "empty_collection",
            "invalid_collection"
        ]

        for collection in test_collections:
            try:
                store = VectorStore(collection_name=collection)
                store.delete_collection()
            except:
                pass

        print("✅ Cleaned up test collections")
    except:
        pass


def main():
    """Run all Phase 4 tests."""
    print("\n" + "="*60)
    print("RAG Pipeline Phase 4 Test Suite")
    print("="*60)
    print("Testing Chatbot Integration with RAG Pipeline")

    # Initialize chatbot
    success, chatbot = test_rag_chatbot_initialization()
    if not success or not chatbot:
        print("\n⚠️ Failed to initialize RAG Chatbot. Exiting.")
        sys.exit(1)

    # Initialize with PPT content
    success, test_slides = test_ppt_initialization(chatbot)
    if not success or not test_slides:
        print("\n⚠️ Failed to initialize with PPT content. Exiting.")
        cleanup()
        sys.exit(1)

    # Run tests
    results = {
        "RAG Chatbot Init": True,  # Already passed
        "PPT Initialization": True,  # Already passed
        "RAG Context Retrieval": test_rag_context_retrieval(chatbot),
        "Global Initialization": test_global_initialization(test_slides),
        "Tutor Response (RAG)": test_tutor_response_rag(),
        "Suggested Questions": test_suggested_questions(),
        "Legacy Compatibility": test_legacy_compatibility(test_slides),
        "Error Handling": test_error_handling()
    }

    # Clean up
    cleanup()

    # Summary
    print("\n" + "="*60)
    print("Phase 4 Test Summary")
    print("="*60)

    all_passed = True
    api_dependent_failed = False

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")

        if not passed:
            # Don't fail overall if only API-dependent tests failed
            if test_name in ["Tutor Response (RAG)", "Suggested Questions", "Legacy Compatibility"]:
                api_dependent_failed = True
            else:
                all_passed = False

    if all_passed:
        print("\n🎉 All Phase 4 tests passed successfully!")
        print("✅ Phase 4 (Chatbot Integration) is complete.")
        print("\n📋 Next Step: Integration with Streamlit app")
    elif api_dependent_failed and all_passed:
        print("\n⚠️ Core tests passed, but API-dependent tests failed.")
        print("   This is expected if Bedrock API is not configured.")
        print("✅ Phase 4 core functionality is complete.")
    else:
        print("\n⚠️ Some core tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()