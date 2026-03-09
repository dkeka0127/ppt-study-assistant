"""
Vector Store Module for RAG Pipeline
ChromaDB wrapper for vector storage and retrieval
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import numpy as np
import uuid
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """ChromaDB wrapper for vector storage and retrieval."""

    def __init__(self, persist_directory: str = "./data/chroma_db", collection_name: str = None):
        """
        Initialize ChromaDB client.

        Args:
            persist_directory: Directory to persist vector database
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collection = None
        self.collection_name = collection_name

        if collection_name:
            self.create_or_get_collection(collection_name)

        logger.info(f"Vector store initialized at {persist_directory}")

    def create_or_get_collection(self, collection_name: str, embedding_function=None):
        """
        Create new collection or get existing one.

        Args:
            collection_name: Name of the collection
            embedding_function: Optional custom embedding function

        Returns:
            ChromaDB collection object
        """
        try:
            # Get or create collection with cosine similarity
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=embedding_function
            )
            self.collection_name = collection_name
            logger.info(f"Collection '{collection_name}' ready with {self.collection.count()} documents")
            return self.collection
        except Exception as e:
            logger.error(f"Error creating/getting collection: {e}")
            raise

    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ) -> None:
        """
        Add documents to collection.

        Args:
            texts: List of document texts
            embeddings: Numpy array of embeddings
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        if not self.collection:
            raise ValueError("No collection selected. Call create_or_get_collection first.")

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        if metadatas is None:
            metadatas = [{}] * len(texts)

        # Ensure embeddings is in the right format
        if isinstance(embeddings, np.ndarray):
            embeddings_list = embeddings.tolist()
        else:
            embeddings_list = embeddings

        try:
            # Add documents to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter: Dict = None
    ) -> Dict[str, Any]:
        """
        Semantic search in collection.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            Dictionary with search results
        """
        if not self.collection:
            raise ValueError("No collection selected")

        # Convert numpy array to list
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.tolist()

        try:
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count() or 1),
                where=filter
            )

            # Format results
            formatted_results = {
                'documents': results.get('documents', [[]]),
                'metadatas': results.get('metadatas', [[]]),
                'distances': results.get('distances', [[]]),
                'ids': results.get('ids', [[]])
            }

            logger.info(f"Search returned {len(formatted_results['documents'][0])} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise

    def hybrid_search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = 10,
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        """
        Hybrid search combining semantic and keyword search.

        Args:
            query: Text query for keyword search
            query_embedding: Query embedding for semantic search
            top_k: Number of results to return
            alpha: Weight for semantic search (1-alpha for keyword)

        Returns:
            Dictionary with search results
        """
        if not self.collection:
            raise ValueError("No collection selected")

        # For now, just use semantic search
        # ChromaDB doesn't have built-in keyword search
        # This would need to be implemented with additional indexing
        logger.info("Performing semantic search (hybrid not fully implemented)")
        return self.search(query_embedding, top_k * 2)

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Get a specific document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document data
        """
        if not self.collection:
            raise ValueError("No collection selected")

        try:
            result = self.collection.get(ids=[doc_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0] if result['documents'] else None,
                    'metadata': result['metadatas'][0] if result['metadatas'] else {},
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise

    def update_document(self, doc_id: str, text: str = None, metadata: Dict = None, embedding: np.ndarray = None) -> None:
        """
        Update a document in the collection.

        Args:
            doc_id: Document ID
            text: New text content
            metadata: New metadata
            embedding: New embedding vector
        """
        if not self.collection:
            raise ValueError("No collection selected")

        try:
            update_args = {'ids': [doc_id]}

            if text is not None:
                update_args['documents'] = [text]
            if metadata is not None:
                update_args['metadatas'] = [metadata]
            if embedding is not None:
                update_args['embeddings'] = [embedding.tolist() if isinstance(embedding, np.ndarray) else embedding]

            self.collection.update(**update_args)
            logger.info(f"Updated document {doc_id}")
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from collection.

        Args:
            ids: List of document IDs to delete
        """
        if not self.collection:
            raise ValueError("No collection selected")

        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.

        Args:
            collection_name: Name of collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            if self.collection_name == collection_name:
                self.collection = None
                self.collection_name = None
            logger.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    def list_collections(self) -> List[str]:
        """
        List all collections in the database.

        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.

        Returns:
            Dictionary with collection statistics
        """
        if not self.collection:
            return {"error": "No collection selected"}

        return {
            "name": self.collection_name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }

    def clear_collection(self) -> None:
        """Clear all documents from the current collection."""
        if not self.collection:
            raise ValueError("No collection selected")

        try:
            # Get all document IDs
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
                logger.info(f"Cleared {len(all_ids)} documents from collection '{self.collection_name}'")
            else:
                logger.info(f"Collection '{self.collection_name}' is already empty")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def reset_database(self) -> None:
        """Reset the entire database (delete all collections)."""
        try:
            # Reset the client (deletes all data)
            self.client.reset()
            self.collection = None
            self.collection_name = None
            logger.warning("Database reset - all collections deleted")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise