"""
Test script for RAG Pipeline Phase 1 Setup
Verifies that embedding service and vector store are working correctly
"""

import sys
import numpy as np
from modules.embedding_service import EmbeddingService, EmbeddingCache
from modules.vector_store import VectorStore

def test_embedding_service():
    """Test embedding service functionality."""
    print("\n" + "="*60)
    print("Testing Embedding Service")
    print("="*60)

    try:
        # Initialize embedding service
        embedder = EmbeddingService()
        print(f"✅ Embedding service initialized")

        # Get model info
        info = embedder.get_model_info()
        print(f"  Model: {info['model_name']}")
        print(f"  Dimension: {info['dimension']}")
        print(f"  Device: {info['device']}")
        print(f"  Max sequence length: {info['max_seq_length']}")

        # Test single text embedding
        test_text = "This is a test sentence for embedding."
        embedding = embedder.embed_text(test_text)
        print(f"\n✅ Single text embedding successful")
        print(f"  Input: '{test_text[:50]}...'")
        print(f"  Embedding shape: {embedding.shape}")
        print(f"  Embedding sample: {embedding[:5]}")

        # Test batch embedding
        test_texts = [
            "First test sentence.",
            "Second test sentence with more words.",
            "Third test sentence.",
            ""  # Test empty text handling
        ]
        batch_embeddings = embedder.embed_batch(test_texts)
        print(f"\n✅ Batch embedding successful")
        print(f"  Batch size: {len(test_texts)}")
        print(f"  Embeddings shape: {batch_embeddings.shape}")

        # Verify dimension consistency
        assert embedding.shape[0] == info['dimension'], "Dimension mismatch"
        assert batch_embeddings.shape == (len(test_texts), info['dimension']), "Batch dimension mismatch"

        print("\n✅ All embedding service tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Embedding service test failed: {e}")
        return False


def test_embedding_cache():
    """Test embedding cache functionality."""
    print("\n" + "="*60)
    print("Testing Embedding Cache")
    print("="*60)

    try:
        # Initialize cache
        cache = EmbeddingCache(max_size=3)
        print(f"✅ Embedding cache initialized (max_size=3)")

        # Test adding to cache
        test_embedding = np.random.randn(384)
        cache.set("test1", test_embedding)
        cache.set("test2", np.random.randn(384))
        cache.set("test3", np.random.randn(384))
        print(f"✅ Added 3 embeddings to cache")

        # Test cache retrieval
        retrieved = cache.get("test1")
        assert retrieved is not None, "Failed to retrieve from cache"
        assert np.array_equal(retrieved, test_embedding), "Retrieved embedding doesn't match"
        print(f"✅ Cache retrieval successful")

        # Test LRU eviction
        cache.set("test4", np.random.randn(384))  # Should evict test2
        assert cache.get("test2") is None, "LRU eviction failed"
        assert cache.get("test1") is not None, "Wrong item evicted"
        print(f"✅ LRU eviction working correctly")

        # Get cache stats
        stats = cache.get_stats()
        print(f"\n✅ Cache stats: {stats}")

        print("\n✅ All cache tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Cache test failed: {e}")
        return False


def test_vector_store():
    """Test vector store functionality."""
    print("\n" + "="*60)
    print("Testing Vector Store")
    print("="*60)

    try:
        # Initialize vector store
        vector_store = VectorStore(
            persist_directory="./data/test_chroma_db",
            collection_name="test_collection"
        )
        print(f"✅ Vector store initialized")

        # Clear collection for clean test
        vector_store.clear_collection()
        print(f"✅ Collection cleared")

        # Test adding documents
        texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing helps computers understand human language.",
            "Computer vision enables machines to interpret visual information."
        ]

        # Generate embeddings
        embedder = EmbeddingService()
        embeddings = embedder.embed_batch(texts)

        # Create metadata
        metadatas = [
            {"topic": "ML", "slide_num": 1},
            {"topic": "DL", "slide_num": 2},
            {"topic": "NLP", "slide_num": 3},
            {"topic": "CV", "slide_num": 4}
        ]

        # Add to vector store
        vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"✅ Added {len(texts)} documents to vector store")

        # Test search
        query = "What is deep learning?"
        query_embedding = embedder.embed_text(query)
        results = vector_store.search(query_embedding, top_k=2)

        print(f"\n✅ Search successful")
        print(f"  Query: '{query}'")
        print(f"  Results returned: {len(results['documents'][0])}")
        if results['documents'][0]:
            print(f"  Top result: '{results['documents'][0][0][:50]}...'")
            print(f"  Distance: {results['distances'][0][0]:.4f}")

        # Test collection stats
        stats = vector_store.get_collection_stats()
        print(f"\n✅ Collection stats: {stats}")

        # List all collections
        collections = vector_store.list_collections()
        print(f"✅ Collections in database: {collections}")

        # Cleanup
        vector_store.delete_collection("test_collection")
        print(f"✅ Test collection deleted")

        print("\n✅ All vector store tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test integration between embedding service and vector store."""
    print("\n" + "="*60)
    print("Testing Integration")
    print("="*60)

    try:
        # Initialize components
        embedder = EmbeddingService()
        vector_store = VectorStore(collection_name="integration_test")

        # Clear collection
        vector_store.clear_collection()

        # Simulate PPT content
        ppt_content = [
            {"slide_num": 1, "text": "Introduction to Python Programming"},
            {"slide_num": 2, "text": "Variables and data types in Python"},
            {"slide_num": 3, "text": "Control flow: if statements and loops"},
            {"slide_num": 4, "text": "Functions and modules in Python"},
            {"slide_num": 5, "text": "Object-oriented programming concepts"}
        ]

        # Process and add to vector store
        texts = [slide["text"] for slide in ppt_content]
        metadatas = [{"slide_num": slide["slide_num"]} for slide in ppt_content]
        embeddings = embedder.embed_batch(texts)

        vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"✅ Indexed {len(ppt_content)} slides")

        # Test retrieval
        query = "How to use functions in Python?"
        query_embedding = embedder.embed_text(query)
        results = vector_store.search(query_embedding, top_k=3)

        print(f"\n✅ Retrieved relevant slides for query: '{query}'")
        for i, (doc, dist, meta) in enumerate(zip(
            results['documents'][0],
            results['distances'][0],
            results['metadatas'][0]
        )):
            print(f"  {i+1}. Slide {meta.get('slide_num', '?')}: {doc}")
            print(f"     Relevance score: {1 - dist:.4f}")

        # Cleanup
        vector_store.delete_collection("integration_test")

        print("\n✅ Integration test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("RAG Pipeline Phase 1 Setup Test")
    print("="*60)

    results = {
        "Embedding Service": test_embedding_service(),
        "Embedding Cache": test_embedding_cache(),
        "Vector Store": test_vector_store(),
        "Integration": test_integration()
    }

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All Phase 1 tests passed successfully!")
        print("✅ Phase 1 setup is complete and working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()