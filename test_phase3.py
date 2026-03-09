"""
Test script for RAG Pipeline Phase 3
Tests RAG Manager integration
"""

import sys
import numpy as np
from modules.rag_manager import RAGManager
from modules.document_processor import Document
import json
import os


def test_rag_manager_initialization():
    """Test RAG Manager initialization."""
    print("\n" + "="*60)
    print("Testing RAG Manager Initialization")
    print("="*60)

    try:
        # Initialize RAG Manager
        rag_manager = RAGManager(
            collection_name="test_rag_collection",
            chunk_size=200,
            chunk_overlap=50,
            use_cache=True
        )
        print("✅ RAG Manager initialized successfully")

        # Check components
        assert rag_manager.embedding_service is not None, "Embedding service not initialized"
        assert rag_manager.vector_store is not None, "Vector store not initialized"
        assert rag_manager.document_processor is not None, "Document processor not initialized"
        assert rag_manager.reranking_service is not None, "Re-ranking service not initialized"
        assert rag_manager.embedding_cache is not None, "Embedding cache not initialized"

        print("✅ All components initialized correctly")

        # Get initial statistics
        stats = rag_manager.get_statistics()
        print(f"\n📊 Initial Statistics:")
        for key, value in stats.items():
            if not isinstance(value, dict):
                print(f"    {key}: {value}")

        print("\n✅ RAG Manager initialization test passed!")
        return True, rag_manager

    except Exception as e:
        print(f"\n❌ RAG Manager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_document_processing(rag_manager):
    """Test document processing in RAG pipeline."""
    print("\n" + "="*60)
    print("Testing Document Processing")
    print("="*60)

    try:
        # Clear collection first
        rag_manager.clear_collection()
        print("✅ Collection cleared")

        # Test PPT data
        test_slides = [
            {
                "slide_num": 1,
                "texts": [
                    "Introduction to RAG (Retrieval Augmented Generation)",
                    "RAG combines the power of retrieval systems with generative models.",
                    "It retrieves relevant information from a knowledge base before generating responses."
                ],
                "tables": [
                    [["Component", "Purpose"],
                     ["Retriever", "Find relevant documents"],
                     ["Generator", "Create responses using context"]]
                ],
                "vision_analysis": "Architecture diagram showing retrieval and generation flow"
            },
            {
                "slide_num": 2,
                "texts": [
                    "Key Components of RAG",
                    "1. Document Store: Stores all the knowledge",
                    "2. Embedding Model: Converts text to vectors",
                    "3. Vector Database: Efficient similarity search",
                    "4. Re-ranker: Improves relevance of results",
                    "5. LLM: Generates final response"
                ],
                "tables": [],
                "vision_analysis": ""
            },
            {
                "slide_num": 3,
                "texts": [
                    "Benefits of RAG",
                    "• Reduced hallucination",
                    "• Up-to-date information",
                    "• Source attribution",
                    "• Scalable knowledge base"
                ],
                "tables": [],
                "vision_analysis": "Comparison chart: Traditional LLM vs RAG-enhanced LLM"
            },
            {
                "slide_num": 4,
                "texts": [
                    "RAG Implementation Best Practices",
                    "Choose appropriate chunk size based on your use case",
                    "Use hybrid search for better results",
                    "Implement re-ranking for improved relevance",
                    "Monitor and optimize retrieval quality"
                ],
                "tables": [],
                "vision_analysis": ""
            }
        ]

        # Process documents
        result = rag_manager.process_document(test_slides, merge_small_chunks=False)
        print(f"✅ {result}")

        # Get statistics
        stats = rag_manager.get_statistics()
        print(f"\n📊 After Processing:")
        print(f"    Documents processed: {stats['documents_processed']}")
        if 'collection_stats' in stats:
            print(f"    Collection count: {stats['collection_stats']['count']}")

        print("\n✅ Document processing test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Document processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval(rag_manager):
    """Test document retrieval."""
    print("\n" + "="*60)
    print("Testing Document Retrieval")
    print("="*60)

    try:
        # Test queries
        test_queries = [
            "What are the components of RAG?",
            "How does retrieval augmented generation reduce hallucination?",
            "What is the purpose of re-ranking?",
            "Best practices for RAG implementation"
        ]

        for query in test_queries:
            print(f"\n📝 Query: '{query}'")

            # Retrieve documents
            documents = rag_manager.retrieve(query, top_k=5)
            print(f"✅ Retrieved {len(documents)} documents")

            if documents:
                # Show top result
                top_doc = documents[0]
                print(f"    Top result (Score: {top_doc.score:.4f}):")
                print(f"    Slide {top_doc.metadata.get('slide_num', '?')}: "
                      f"'{top_doc.content[:80]}...'")

        # Test with metadata filter
        print("\n📝 Testing filtered retrieval (slide_num=2):")
        filtered_docs = rag_manager.retrieve(
            "components",
            top_k=3,
            filter_metadata={"slide_num": 2}
        )
        print(f"✅ Retrieved {len(filtered_docs)} documents with filter")

        print("\n✅ Document retrieval test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Document retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reranking(rag_manager):
    """Test re-ranking functionality."""
    print("\n" + "="*60)
    print("Testing Re-ranking")
    print("="*60)

    try:
        query = "What are the benefits of using RAG over traditional LLMs?"

        # Retrieve documents
        retrieved_docs = rag_manager.retrieve(query, top_k=10)
        print(f"✅ Retrieved {len(retrieved_docs)} documents")

        if retrieved_docs:
            # Show scores before re-ranking
            print("\n📊 Before re-ranking (top 3):")
            for i, doc in enumerate(retrieved_docs[:3]):
                print(f"    {i+1}. Score: {doc.score:.4f}, "
                      f"Slide {doc.metadata.get('slide_num', '?')}")

            # Re-rank documents
            reranked_docs = rag_manager.rerank(query, retrieved_docs, top_n=5)
            print(f"\n✅ Re-ranked to top {len(reranked_docs)} documents")

            # Show scores after re-ranking
            print("\n📊 After re-ranking:")
            for i, doc in enumerate(reranked_docs):
                print(f"    {i+1}. Score: {doc.score:.4f}, "
                      f"Slide {doc.metadata.get('slide_num', '?')}: "
                      f"'{doc.content[:50]}...'")

            # Test with diversity
            diverse_docs = rag_manager.rerank(
                query,
                retrieved_docs,
                top_n=5,
                use_diversity=True
            )
            print(f"\n✅ Diversity re-ranking: {len(diverse_docs)} documents")

        print("\n✅ Re-ranking test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Re-ranking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_generation(rag_manager):
    """Test context generation for LLM."""
    print("\n" + "="*60)
    print("Testing Context Generation")
    print("="*60)

    try:
        query = "Explain the complete RAG architecture and its benefits"

        # Get context
        context, sources = rag_manager.get_context(
            query,
            max_tokens=1000,
            top_k_retrieve=10,
            top_n_rerank=3,
            use_diversity=False
        )

        print(f"✅ Generated context ({len(context)} chars)")
        print(f"✅ Included {len(sources)} source documents")

        # Display context preview
        print("\n📄 Context Preview:")
        print("-" * 40)
        print(context[:500] + "..." if len(context) > 500 else context)
        print("-" * 40)

        # Display sources
        print("\n📚 Sources:")
        for i, source in enumerate(sources):
            print(f"    {i+1}. Slide {source['slide_num']}, "
                  f"Type: {source['content_type']}, "
                  f"Score: {source['score']}")

        print("\n✅ Context generation test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Context generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_caching(rag_manager):
    """Test embedding cache functionality."""
    print("\n" + "="*60)
    print("Testing Embedding Cache")
    print("="*60)

    try:
        # Reset cache statistics
        initial_stats = rag_manager.get_statistics()
        initial_hits = initial_stats.get("cache_hits", 0)
        initial_misses = initial_stats.get("cache_misses", 0)

        # First query (cache miss)
        test_text = "This is a test query for caching"
        _ = rag_manager.retrieve(test_text, top_k=1)

        # Same query again (cache hit)
        _ = rag_manager.retrieve(test_text, top_k=1)

        # Get updated statistics
        final_stats = rag_manager.get_statistics()
        final_hits = final_stats.get("cache_hits", 0)
        final_misses = final_stats.get("cache_misses", 0)

        print(f"✅ Cache statistics:")
        print(f"    Cache hits: {final_hits - initial_hits}")
        print(f"    Cache misses: {final_misses - initial_misses}")

        if final_stats.get("cache_hit_rate") is not None:
            print(f"    Hit rate: {final_stats['cache_hit_rate']:.2%}")

        print("\n✅ Caching test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state_persistence(rag_manager):
    """Test saving and loading RAG state."""
    print("\n" + "="*60)
    print("Testing State Persistence")
    print("="*60)

    try:
        # Save state
        state_file = "./data/test_rag_state.json"
        rag_manager.save_state(state_file)
        print(f"✅ Saved state to {state_file}")

        # Load and verify state file
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                saved_state = json.load(f)

            print(f"✅ State file contains:")
            print(f"    Collection: {saved_state.get('collection_name')}")
            print(f"    Chunk size: {saved_state.get('chunk_size')}")
            print(f"    Documents: {saved_state.get('statistics', {}).get('documents_processed')}")

            # Clean up
            os.remove(state_file)
            print(f"✅ Cleaned up state file")

        print("\n✅ State persistence test passed!")
        return True

    except Exception as e:
        print(f"\n❌ State persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end(rag_manager):
    """Test complete RAG pipeline end-to-end."""
    print("\n" + "="*60)
    print("Testing End-to-End RAG Pipeline")
    print("="*60)

    try:
        # User query
        user_query = "How does RAG improve the accuracy of AI responses compared to traditional methods?"

        print(f"🔍 User Query: '{user_query}'")
        print("\n" + "-"*40)

        # Get context using full pipeline
        context, sources = rag_manager.get_context(
            user_query,
            max_tokens=1500,
            top_k_retrieve=10,
            top_n_rerank=4,
            use_diversity=True
        )

        print(f"\n✅ Pipeline Results:")
        print(f"    Context length: {len(context)} characters")
        print(f"    Sources used: {len(sources)}")
        print(f"    Queries processed: {rag_manager.stats['queries_processed']}")

        # Display final context
        print("\n📄 Generated Context for LLM:")
        print("="*40)
        print(context)
        print("="*40)

        # Display source attribution
        print("\n📚 Source Attribution:")
        for i, source in enumerate(sources):
            print(f"    [{i+1}] Slide {source['slide_num']} "
                  f"({source['content_type']}) - "
                  f"Relevance: {source['score']:.2f}")

        # Get final statistics
        final_stats = rag_manager.get_statistics()
        print(f"\n📊 Final Pipeline Statistics:")
        print(f"    Documents in collection: {final_stats.get('collection_stats', {}).get('count', 0)}")
        print(f"    Total queries: {final_stats['queries_processed']}")
        print(f"    Cache hit rate: {final_stats.get('cache_hit_rate', 0):.2%}")

        print("\n✅ End-to-end test passed!")
        return True

    except Exception as e:
        print(f"\n❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup(rag_manager):
    """Clean up test resources."""
    try:
        if rag_manager:
            rag_manager.delete_collection()
            print("✅ Cleaned up test collection")
    except:
        pass


def main():
    """Run all Phase 3 tests."""
    print("\n" + "="*60)
    print("RAG Pipeline Phase 3 Test Suite")
    print("="*60)
    print("Testing RAG Manager Integration")

    # Initialize RAG Manager
    success, rag_manager = test_rag_manager_initialization()
    if not success or not rag_manager:
        print("\n⚠️ Failed to initialize RAG Manager. Exiting.")
        sys.exit(1)

    # Run tests
    results = {
        "Initialization": success,
        "Document Processing": test_document_processing(rag_manager),
        "Retrieval": test_retrieval(rag_manager),
        "Re-ranking": test_reranking(rag_manager),
        "Context Generation": test_context_generation(rag_manager),
        "Caching": test_caching(rag_manager),
        "State Persistence": test_state_persistence(rag_manager),
        "End-to-End": test_end_to_end(rag_manager)
    }

    # Clean up
    cleanup(rag_manager)

    # Summary
    print("\n" + "="*60)
    print("Phase 3 Test Summary")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All Phase 3 tests passed successfully!")
        print("✅ Phase 3 (RAG Manager Integration) is complete.")
        print("\n📋 Next Step: Phase 4 - Chatbot Integration")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()