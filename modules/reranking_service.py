"""
Re-ranking Service for RAG Pipeline
Cross-encoder based re-ranking for improved relevance
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import sentence_transformers CrossEncoder
try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    logger.warning("sentence_transformers CrossEncoder not available, using fallback implementation")

    # Fallback implementation
    class CrossEncoder:
        def __init__(self, model_name):
            self.model_name = model_name

        def predict(self, pairs):
            # Simple cosine similarity based scoring for fallback
            scores = []
            for query, doc in pairs:
                # Simple keyword matching score
                query_words = set(query.lower().split())
                doc_words = set(doc.lower().split())
                if len(query_words) > 0:
                    score = len(query_words.intersection(doc_words)) / len(query_words)
                else:
                    score = 0.0
                scores.append(score)
            return np.array(scores)


class RerankingService:
    """Cross-encoder based re-ranking service."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder model.

        Args:
            model_name: Name of the cross-encoder model to use
        """
        self.model_name = model_name
        self.model = CrossEncoder(model_name)

        if CROSS_ENCODER_AVAILABLE:
            logger.info(f"Re-ranking service initialized with {model_name}")
        else:
            logger.warning(f"Re-ranking service using fallback implementation")

    def rerank(
        self,
        query: str,
        documents: List,
        top_n: int = 5,
        threshold: float = 0.0
    ) -> List:
        """
        Re-rank documents based on relevance to query.

        Args:
            query: Search query
            documents: List of Document objects to re-rank
            top_n: Number of top documents to return
            threshold: Minimum score threshold

        Returns:
            List of re-ranked documents
        """
        if not documents:
            return []

        # Prepare query-document pairs
        pairs = [(query, doc.content) for doc in documents]

        # Get relevance scores
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            logger.error(f"Error during re-ranking: {e}")
            # Return original order if re-ranking fails
            return documents[:top_n]

        # Add scores to documents
        for doc, score in zip(documents, scores):
            doc.score = float(score)

        # Sort by score (descending) and filter by threshold
        ranked_docs = sorted(documents, key=lambda x: x.score, reverse=True)
        filtered_docs = [doc for doc in ranked_docs if doc.score >= threshold]

        # Return top N documents
        result = filtered_docs[:top_n]

        logger.info(f"Re-ranked {len(documents)} documents, returning top {len(result)}")

        return result

    def score_pairs(self, query: str, texts: List[str]) -> np.ndarray:
        """
        Score query-document pairs.

        Args:
            query: Search query
            texts: List of document texts

        Returns:
            Array of relevance scores
        """
        if not texts:
            return np.array([])

        pairs = [(query, text) for text in texts]

        try:
            scores = self.model.predict(pairs)
            return scores
        except Exception as e:
            logger.error(f"Error scoring pairs: {e}")
            return np.zeros(len(texts))

    def batch_rerank(
        self,
        queries: List[str],
        documents_list: List[List],
        top_n: int = 5
    ) -> List[List]:
        """
        Batch re-ranking for multiple queries.

        Args:
            queries: List of queries
            documents_list: List of document lists (one per query)
            top_n: Number of top documents per query

        Returns:
            List of re-ranked document lists
        """
        results = []

        for query, documents in zip(queries, documents_list):
            ranked = self.rerank(query, documents, top_n)
            results.append(ranked)

        return results

    def get_score_distribution(self, scores: List[float]) -> Dict[str, float]:
        """
        Get statistics about score distribution.

        Args:
            scores: List of relevance scores

        Returns:
            Dictionary with score statistics
        """
        if not scores:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0
            }

        scores_array = np.array(scores)

        return {
            "mean": float(np.mean(scores_array)),
            "std": float(np.std(scores_array)),
            "min": float(np.min(scores_array)),
            "max": float(np.max(scores_array)),
            "median": float(np.median(scores_array))
        }


class DiversityReranker:
    """Re-ranker that balances relevance with diversity."""

    def __init__(self, lambda_param: float = 0.5):
        """
        Initialize diversity re-ranker.

        Args:
            lambda_param: Balance between relevance (1.0) and diversity (0.0)
        """
        self.lambda_param = lambda_param
        logger.info(f"Diversity re-ranker initialized with lambda={lambda_param}")

    def rerank_with_diversity(
        self,
        documents: List,
        top_n: int = 5
    ) -> List:
        """
        Re-rank documents considering both relevance and diversity.

        Args:
            documents: List of documents with scores
            top_n: Number of documents to return

        Returns:
            Re-ranked documents with diversity
        """
        if not documents or len(documents) <= 1:
            return documents[:top_n]

        # Sort by initial score
        sorted_docs = sorted(documents, key=lambda x: x.score, reverse=True)

        # Greedy selection for diversity
        selected = [sorted_docs[0]]
        candidates = sorted_docs[1:]

        while len(selected) < top_n and candidates:
            # Calculate diversity scores
            diversity_scores = []

            for candidate in candidates:
                # Calculate similarity to already selected documents
                similarities = []
                for selected_doc in selected:
                    # Simple Jaccard similarity based on words
                    candidate_words = set(candidate.content.lower().split())
                    selected_words = set(selected_doc.content.lower().split())

                    if len(candidate_words.union(selected_words)) > 0:
                        similarity = len(candidate_words.intersection(selected_words)) / \
                                   len(candidate_words.union(selected_words))
                    else:
                        similarity = 0.0

                    similarities.append(similarity)

                # Diversity is inverse of maximum similarity
                max_similarity = max(similarities) if similarities else 0.0
                diversity = 1.0 - max_similarity

                # Combined score
                combined_score = (self.lambda_param * candidate.score +
                                (1 - self.lambda_param) * diversity)

                diversity_scores.append((candidate, combined_score))

            # Select document with highest combined score
            diversity_scores.sort(key=lambda x: x[1], reverse=True)
            selected_doc = diversity_scores[0][0]
            selected.append(selected_doc)
            candidates.remove(selected_doc)

        logger.info(f"Selected {len(selected)} diverse documents from {len(documents)}")
        return selected