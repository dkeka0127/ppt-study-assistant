"""
Test script for RAG Pipeline Phase 2
Tests Document Processor and Re-ranking Service
"""

import sys
import numpy as np
from modules.document_processor import DocumentProcessor, Document
from modules.reranking_service import RerankingService, DiversityReranker


def test_document_processor():
    """Test document processor functionality."""
    print("\n" + "="*60)
    print("Testing Document Processor")
    print("="*60)

    try:
        # Initialize processor
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        print("✅ Document processor initialized")

        # Test data - simulate PPT slides
        test_slides = [
            {
                "slide_num": 1,
                "texts": [
                    "Introduction to Machine Learning",
                    "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
                    "It focuses on the development of computer programs that can access data and use it to learn for themselves."
                ],
                "tables": [
                    [["Type", "Description"],
                     ["Supervised", "Learning with labeled data"],
                     ["Unsupervised", "Learning without labels"],
                     ["Reinforcement", "Learning through rewards"]]
                ],
                "vision_analysis": "Diagram showing the relationship between AI, ML, and Deep Learning"
            },
            {
                "slide_num": 2,
                "texts": [
                    "Deep Learning Fundamentals",
                    "Deep learning is a subset of machine learning that uses neural networks with multiple layers.",
                    "These neural networks attempt to simulate the behavior of the human brain."
                ],
                "tables": [],
                "vision_analysis": ""
            },
            {
                "slide_num": 3,
                "texts": [
                    "Applications of Machine Learning",
                    "• Natural Language Processing (NLP)",
                    "• Computer Vision",
                    "• Recommendation Systems",
                    "• Autonomous Vehicles",
                    "• Healthcare Diagnostics"
                ],
                "tables": [],
                "vision_analysis": "Icons representing different ML applications"
            }
        ]

        # Process slides
        documents = processor.process_slides(test_slides)
        print(f"✅ Processed {len(test_slides)} slides into {len(documents)} documents")

        # Display sample documents
        print("\n📄 Sample Documents:")
        for i, doc in enumerate(documents[:3]):
            print(f"\n  Document {i+1}:")
            print(f"    Content: '{doc.content[:80]}...'")
            print(f"    Metadata: slide_num={doc.metadata.get('slide_num')}, "
                  f"type={doc.metadata.get('content_type')}, "
                  f"chunk_index={doc.metadata.get('chunk_index', 'N/A')}")

        # Test chunking
        long_text = "This is a very long text. " * 50  # 500+ characters
        chunks = processor.chunk_text(long_text, {"slide_num": 99})
        print(f"\n✅ Chunking test: {len(long_text)} chars → {len(chunks)} chunks")

        # Test merging
        merged = processor.merge_documents(documents[:5], max_size=300)
        print(f"✅ Merging test: {len(documents[:5])} documents → {len(merged)} merged")

        # Test keyword extraction
        sample_text = documents[0].content if documents else "machine learning deep learning neural network"
        keywords = processor.extract_keywords(sample_text, top_k=5)
        print(f"✅ Keywords extracted: {keywords}")

        # Get statistics
        stats = processor.get_statistics(documents)
        print(f"\n📊 Processing Statistics:")
        for key, value in stats.items():
            print(f"    {key}: {value}")

        print("\n✅ All document processor tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Document processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reranking_service():
    """Test re-ranking service functionality."""
    print("\n" + "="*60)
    print("Testing Re-ranking Service")
    print("="*60)

    try:
        # Initialize re-ranker
        reranker = RerankingService()
        print("✅ Re-ranking service initialized")

        # Create test documents
        test_documents = [
            Document(
                content="Deep learning uses neural networks with multiple layers to learn from data",
                metadata={"slide_num": 1}
            ),
            Document(
                content="Machine learning is a subset of artificial intelligence",
                metadata={"slide_num": 2}
            ),
            Document(
                content="Neural networks are inspired by the human brain structure",
                metadata={"slide_num": 3}
            ),
            Document(
                content="Python is a popular programming language for data science",
                metadata={"slide_num": 4}
            ),
            Document(
                content="Deep neural networks can have hundreds of layers",
                metadata={"slide_num": 5}
            )
        ]

        # Add initial scores (simulating vector search results)
        for i, doc in enumerate(test_documents):
            doc.score = 0.5 + (0.1 * (len(test_documents) - i))

        print(f"✅ Created {len(test_documents)} test documents")

        # Test re-ranking
        query = "What is deep learning neural network?"
        reranked = reranker.rerank(query, test_documents, top_n=3)

        print(f"\n✅ Re-ranking results for query: '{query}'")
        for i, doc in enumerate(reranked):
            print(f"  {i+1}. Score: {doc.score:.4f}")
            print(f"     Content: '{doc.content[:60]}...'")

        # Test score pairs
        texts = [doc.content for doc in test_documents]
        scores = reranker.score_pairs(query, texts)
        print(f"\n✅ Score pairs test: Generated {len(scores)} scores")
        print(f"    Score range: [{scores.min():.4f}, {scores.max():.4f}]")

        print("\n✅ All re-ranking tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Re-ranking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_diversity_reranker():
    """Test diversity re-ranker functionality."""
    print("\n" + "="*60)
    print("Testing Diversity Re-ranker")
    print("="*60)

    try:
        # Initialize diversity re-ranker
        div_reranker = DiversityReranker(lambda_param=0.7)
        print("✅ Diversity re-ranker initialized")

        # Create test documents with varying similarity
        test_documents = [
            Document(content="Deep learning and neural networks", metadata={"id": 1}, score=0.9),
            Document(content="Deep learning with neural networks", metadata={"id": 2}, score=0.85),  # Similar to 1
            Document(content="Machine learning algorithms", metadata={"id": 3}, score=0.8),
            Document(content="Python programming for data science", metadata={"id": 4}, score=0.75),
            Document(content="Neural network architectures", metadata={"id": 5}, score=0.7),  # Similar to 1,2
        ]

        # Test diversity re-ranking
        diverse_results = div_reranker.rerank_with_diversity(test_documents, top_n=3)

        print(f"\n✅ Diversity re-ranking results (λ=0.7):")
        for i, doc in enumerate(diverse_results):
            print(f"  {i+1}. ID: {doc.metadata['id']}, Score: {doc.score:.2f}")
            print(f"     Content: '{doc.content}'")

        print("\n✅ All diversity re-ranker tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Diversity re-ranker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test integration of document processing and re-ranking."""
    print("\n" + "="*60)
    print("Testing Phase 2 Integration")
    print("="*60)

    try:
        # Initialize components
        processor = DocumentProcessor(chunk_size=150, chunk_overlap=30)
        reranker = RerankingService()

        # Process test PPT data
        test_ppt = [
            {
                "slide_num": 1,
                "texts": [
                    "Introduction to Natural Language Processing",
                    "NLP is a field of AI that focuses on the interaction between computers and human language.",
                    "It enables machines to understand, interpret, and generate human language."
                ]
            },
            {
                "slide_num": 2,
                "texts": [
                    "Key NLP Tasks",
                    "• Text Classification: Categorizing text into predefined classes",
                    "• Named Entity Recognition: Identifying entities in text",
                    "• Sentiment Analysis: Determining emotional tone",
                    "• Machine Translation: Converting text between languages"
                ]
            },
            {
                "slide_num": 3,
                "texts": [
                    "Deep Learning in NLP",
                    "Transformer models like BERT and GPT have revolutionized NLP.",
                    "These models use attention mechanisms to understand context."
                ]
            }
        ]

        # Process documents
        documents = processor.process_slides(test_ppt)
        print(f"✅ Processed {len(test_ppt)} slides into {len(documents)} documents")

        # Simulate initial scoring (would come from vector search)
        for i, doc in enumerate(documents):
            doc.score = np.random.uniform(0.3, 0.9)

        # Re-rank for a specific query
        query = "What are transformer models in NLP?"
        reranked = reranker.rerank(query, documents, top_n=3)

        print(f"\n✅ Integration test - Query: '{query}'")
        print(f"   Retrieved top {len(reranked)} documents after re-ranking:")

        for i, doc in enumerate(reranked):
            print(f"\n  {i+1}. Slide {doc.metadata['slide_num']}, Score: {doc.score:.4f}")
            print(f"     Type: {doc.metadata['content_type']}")
            print(f"     Content: '{doc.content[:100]}...'")

        print("\n✅ Phase 2 integration test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 2 tests."""
    print("\n" + "="*60)
    print("RAG Pipeline Phase 2 Test Suite")
    print("="*60)

    results = {
        "Document Processor": test_document_processor(),
        "Re-ranking Service": test_reranking_service(),
        "Diversity Re-ranker": test_diversity_reranker(),
        "Integration": test_integration()
    }

    # Summary
    print("\n" + "="*60)
    print("Phase 2 Test Summary")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All Phase 2 tests passed successfully!")
        print("✅ Phase 2 (Document Processing Pipeline) is complete.")
        print("\n📋 Next Step: Phase 3 - RAG Manager Integration")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()