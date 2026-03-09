"""
RAG Manager - Central orchestrator for RAG pipeline
Manages document processing, retrieval, and re-ranking
"""

from typing import List, Dict, Any, Tuple, Optional
from modules.embedding_service import EmbeddingService, EmbeddingCache
from modules.vector_store import VectorStore
from modules.document_processor import DocumentProcessor, Document
from modules.reranking_service import RerankingService, DiversityReranker
import logging
import os
import hashlib
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGManager:
    """Central orchestrator for RAG pipeline operations."""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        collection_name: str = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        use_cache: bool = True
    ):
        """
        Initialize RAG components.

        Args:
            embedding_model: Name of the embedding model
            rerank_model: Name of the re-ranking model
            collection_name: Name of the vector database collection
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            use_cache: Whether to use embedding cache
        """
        # Initialize services
        self.embedding_service = EmbeddingService(embedding_model)
        self.vector_store = VectorStore(
            persist_directory="./data/chroma_db",
            collection_name=collection_name
        )
        self.document_processor = DocumentProcessor(chunk_size, chunk_overlap)
        self.reranking_service = RerankingService(rerank_model)
        self.diversity_reranker = DiversityReranker(lambda_param=0.7)

        # Initialize cache if enabled
        self.embedding_cache = EmbeddingCache(max_size=1000) if use_cache else None

        # Store configuration
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_cache = use_cache

        # Statistics tracking
        self.stats = {
            "documents_processed": 0,
            "queries_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

        logger.info(f"RAG Manager initialized with collection: {collection_name}")

    def process_document(
        self,
        slides_data: List[Dict],
        batch_size: int = 32,
        merge_small_chunks: bool = False
    ) -> str:
        """
        Process PPT content into vector database.

        Args:
            slides_data: List of slide dictionaries
            batch_size: Batch size for embedding generation
            merge_small_chunks: Whether to merge small chunks

        Returns:
            Status message
        """
        try:
            # Process slides into documents
            documents = self.document_processor.process_slides(slides_data)

            # Optionally merge small documents
            if merge_small_chunks:
                documents = self.document_processor.merge_documents(
                    documents,
                    max_size=self.chunk_size * 2
                )

            # Generate embeddings with caching
            embeddings_list = []
            for doc in documents:
                embedding = self._get_embedding(doc.content)
                embeddings_list.append(embedding)
                doc.embedding = embedding

            # Convert to numpy array
            import numpy as np
            embeddings = np.array(embeddings_list)

            # Extract metadata and IDs
            metadatas = []
            ids = []
            texts = []

            for i, doc in enumerate(documents):
                # Enhance metadata
                metadata = doc.metadata.copy()
                metadata["processed_at"] = datetime.now().isoformat()
                metadata["embedding_model"] = self.embedding_service.model_name

                metadatas.append(metadata)
                ids.append(doc.metadata.get("chunk_id", f"doc_{i}"))
                texts.append(doc.content)

            # Store in vector database
            self.vector_store.add_documents(
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            # Update statistics
            self.stats["documents_processed"] += len(documents)

            # Get collection stats
            collection_stats = self.vector_store.get_collection_stats()

            logger.info(f"Processed {len(documents)} chunks into vector store")
            return (f"Successfully indexed {len(documents)} chunks. "
                   f"Collection now has {collection_stats.get('count', 0)} total documents.")

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Dict = None,
        use_hybrid: bool = False
    ) -> List[Document]:
        """
        Retrieve relevant documents.

        Args:
            query: Search query
            top_k: Number of documents to retrieve
            filter_metadata: Metadata filters
            use_hybrid: Whether to use hybrid search

        Returns:
            List of retrieved documents
        """
        try:
            # Generate query embedding
            query_embedding = self._get_embedding(query)

            # Perform search
            if use_hybrid:
                results = self.vector_store.hybrid_search(
                    query=query,
                    query_embedding=query_embedding,
                    top_k=top_k
                )
            else:
                results = self.vector_store.search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    filter=filter_metadata
                )

            # Convert results to documents
            documents = []
            if results and 'documents' in results and results['documents']:
                for i in range(len(results['documents'][0])):
                    doc = Document(
                        content=results['documents'][0][i],
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                        score=1 - results['distances'][0][i] if results['distances'] else 0.0
                    )
                    documents.append(doc)

            # Update statistics
            self.stats["queries_processed"] += 1

            logger.info(f"Retrieved {len(documents)} documents for query: '{query[:50]}...'")
            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5,
        use_diversity: bool = False
    ) -> List[Document]:
        """
        Re-rank retrieved documents.

        Args:
            query: Original search query
            documents: Documents to re-rank
            top_n: Number of top documents to return
            use_diversity: Whether to use diversity re-ranking

        Returns:
            Re-ranked documents
        """
        if not documents:
            return []

        try:
            # Apply re-ranking
            reranked = self.reranking_service.rerank(query, documents, top_n=top_n)

            # Optionally apply diversity re-ranking
            if use_diversity and len(reranked) > 1:
                reranked = self.diversity_reranker.rerank_with_diversity(
                    reranked,
                    top_n=top_n
                )

            return reranked

        except Exception as e:
            logger.error(f"Error during re-ranking: {e}")
            # Return original documents if re-ranking fails
            return documents[:top_n]

    def get_context(
        self,
        query: str,
        max_tokens: int = 3000,
        top_k_retrieve: int = 10,
        top_n_rerank: int = 5,
        filter_metadata: Dict = None,
        use_diversity: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Get optimized context for LLM.

        Args:
            query: User query
            max_tokens: Maximum tokens in context
            top_k_retrieve: Number of documents to retrieve
            top_n_rerank: Number of documents after re-ranking
            filter_metadata: Metadata filters
            use_diversity: Whether to use diversity re-ranking

        Returns:
            Tuple of (context_string, source_documents)
        """
        # Retrieve documents
        retrieved_docs = self.retrieve(
            query,
            top_k=top_k_retrieve,
            filter_metadata=filter_metadata
        )

        if not retrieved_docs:
            logger.warning(f"No documents retrieved for query: '{query}'")
            return "", []

        # Re-rank documents
        ranked_docs = self.rerank(
            query,
            retrieved_docs,
            top_n=top_n_rerank,
            use_diversity=use_diversity
        )

        # Prepare context within token limits
        context_parts = []
        sources = []
        current_tokens = 0

        for doc in ranked_docs:
            # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
            doc_tokens = len(doc.content) // 4

            if current_tokens + doc_tokens > max_tokens:
                # Check if we can fit a truncated version
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 50:  # Minimum useful chunk
                    truncated_content = doc.content[:remaining_tokens * 4]
                    context_parts.append(self._format_context_chunk(doc, truncated_content))
                    sources.append(self._create_source_reference(doc))
                break

            context_parts.append(self._format_context_chunk(doc))
            sources.append(self._create_source_reference(doc))
            current_tokens += doc_tokens

        context = "\n\n---\n\n".join(context_parts)

        logger.info(f"Generated context with {len(ranked_docs)} documents, "
                   f"~{current_tokens} tokens")

        return context, sources

    def _get_embedding(self, text: str) -> Any:
        """
        Get embedding with caching support.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache first
        if self.embedding_cache:
            cached = self.embedding_cache.get(text)
            if cached is not None:
                self.stats["cache_hits"] += 1
                return cached
            else:
                self.stats["cache_misses"] += 1

        # Generate embedding
        embedding = self.embedding_service.embed_text(text)

        # Cache the result
        if self.embedding_cache:
            self.embedding_cache.set(text, embedding)

        return embedding

    def _format_context_chunk(self, doc: Document, content: str = None) -> str:
        """
        Format a document for context.

        Args:
            doc: Document to format
            content: Optional content override

        Returns:
            Formatted context string
        """
        content = content or doc.content
        slide_num = doc.metadata.get('slide_num', '?')
        content_type = doc.metadata.get('content_type', 'text')

        # Format based on content type
        if content_type == 'table':
            prefix = f"[슬라이드 {slide_num} - 표]"
        elif content_type == 'image_description':
            prefix = f"[슬라이드 {slide_num} - 이미지]"
        else:
            prefix = f"[슬라이드 {slide_num}]"

        return f"{prefix}\n{content}"

    def _create_source_reference(self, doc: Document) -> Dict[str, Any]:
        """
        Create source reference for a document.

        Args:
            doc: Document to reference

        Returns:
            Source reference dictionary
        """
        return {
            'slide_num': doc.metadata.get('slide_num', '?'),
            'content_type': doc.metadata.get('content_type', 'text'),
            'chunk_index': doc.metadata.get('chunk_index', 0),
            'score': round(doc.score, 4) if doc.score else 0.0,
            'has_table': doc.metadata.get('has_table', False),
            'has_image': doc.metadata.get('has_image', False)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get RAG pipeline statistics.

        Returns:
            Statistics dictionary
        """
        stats = self.stats.copy()

        # Add collection statistics
        if self.vector_store.collection:
            stats["collection_stats"] = self.vector_store.get_collection_stats()

        # Add cache statistics
        if self.embedding_cache:
            cache_stats = self.embedding_cache.get_stats()
            stats["cache_stats"] = cache_stats
            if self.stats["cache_hits"] + self.stats["cache_misses"] > 0:
                stats["cache_hit_rate"] = self.stats["cache_hits"] / \
                    (self.stats["cache_hits"] + self.stats["cache_misses"])

        return stats

    def clear_collection(self) -> None:
        """Clear all documents from the current collection."""
        if self.vector_store.collection:
            self.vector_store.clear_collection()
            self.stats["documents_processed"] = 0
            logger.info(f"Cleared collection: {self.collection_name}")

    def delete_collection(self) -> None:
        """Delete the current collection."""
        if self.collection_name:
            self.vector_store.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")

    def save_state(self, filepath: str) -> None:
        """
        Save RAG manager state to file.

        Args:
            filepath: Path to save state
        """
        state = {
            "collection_name": self.collection_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "statistics": self.get_statistics(),
            "timestamp": datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Saved RAG state to {filepath}")

    @classmethod
    def load_state(cls, filepath: str) -> 'RAGManager':
        """
        Load RAG manager from saved state.

        Args:
            filepath: Path to load state from

        Returns:
            Initialized RAG manager
        """
        with open(filepath, 'r') as f:
            state = json.load(f)

        manager = cls(
            collection_name=state.get("collection_name"),
            chunk_size=state.get("chunk_size", 500),
            chunk_overlap=state.get("chunk_overlap", 100)
        )

        logger.info(f"Loaded RAG state from {filepath}")
        return manager