"""
Embedding Service for RAG Pipeline
Handles text embedding generation using sentence-transformers
"""

import numpy as np
from typing import List, Optional
import logging
import hashlib

# Try to import sentence_transformers, fallback to mock if not available
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    # Mock implementation for testing
    class SentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
            self.max_seq_length = 256

        def encode(self, text, convert_to_numpy=True, batch_size=32, show_progress_bar=False):
            # Simple hash-based embedding for testing
            if isinstance(text, str):
                hash_obj = hashlib.sha256(text.encode())
                hash_bytes = hash_obj.digest()
                # Convert to 384-dim vector (matching all-MiniLM-L6-v2)
                embedding = np.frombuffer(hash_bytes, dtype=np.uint8)
                embedding = np.pad(embedding, (0, 384 - len(embedding)), mode='wrap')
                return embedding.astype(np.float32) / 255.0
            else:
                return np.array([self.encode(t) for t in text])

        def get_sentence_embedding_dimension(self):
            return 384

        def to(self, device):
            pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Handles text embedding generation using sentence-transformers."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model.

        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
        else:
            self.device = "cpu"
            logger.warning("sentence-transformers not available, using mock implementation")

        logger.info(f"Embedding service initialized with {model_name} on {self.device}")
        logger.info(f"Embedding dimension: {self.dimension}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text.

        Args:
            text: Input text to embed

        Returns:
            Numpy array of embedding vector
        """
        if not text.strip():
            logger.warning("Empty text provided for embedding")
            return np.zeros(self.dimension)

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            Numpy array of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding")
            return np.array([])

        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            logger.warning("All texts in batch were empty")
            return np.zeros((len(texts), self.dimension))

        try:
            # Generate embeddings for valid texts
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(valid_texts) > 100
            )

            # Create full result array with zeros for empty texts
            result = np.zeros((len(texts), self.dimension))
            for i, idx in enumerate(valid_indices):
                result[idx] = embeddings[i]

            logger.info(f"Generated embeddings for {len(valid_texts)}/{len(texts)} texts")
            return result

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get embedding vector dimension.

        Returns:
            Dimension of the embedding vectors
        """
        return self.dimension

    def get_model_info(self) -> dict:
        """
        Get information about the embedding model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "device": self.device,
            "max_seq_length": self.model.max_seq_length
        }


class EmbeddingCache:
    """LRU cache for embeddings to avoid recomputation."""

    def __init__(self, max_size: int = 1000):
        """
        Initialize embedding cache.

        Args:
            max_size: Maximum number of cached embeddings
        """
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
        logger.info(f"Embedding cache initialized with max_size={max_size}")

    def _get_key(self, text: str) -> str:
        """
        Generate cache key from text.

        Args:
            text: Input text

        Returns:
            Hash key for the text
        """
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[np.ndarray]:
        """
        Get cached embedding if exists.

        Args:
            text: Input text

        Returns:
            Cached embedding or None
        """
        key = self._get_key(text)
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, text: str, embedding: np.ndarray) -> None:
        """
        Cache an embedding.

        Args:
            text: Input text
            embedding: Embedding vector to cache
        """
        key = self._get_key(text)

        # Check if already in cache
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return

        # Remove oldest if at max capacity
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        # Add new embedding
        self.cache[key] = embedding
        self.access_order.append(key)

    def clear(self) -> None:
        """Clear all cached embeddings."""
        self.cache.clear()
        self.access_order.clear()
        logger.info("Embedding cache cleared")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": 0.0  # Would need to track hits/misses for this
        }