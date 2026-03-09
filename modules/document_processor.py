"""
Document Processor for RAG Pipeline
Handles document chunking and metadata extraction
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document representation for RAG pipeline."""
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            'content': self.content,
            'metadata': self.metadata,
            'score': self.score
        }


class DocumentProcessor:
    """Handles document chunking and metadata extraction."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize processor with chunking parameters.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "。", "!", "!", "?", "？", " ", ""],
            length_function=len,
            is_separator_regex=False
        )
        logger.info(f"Document processor initialized with chunk_size={chunk_size}, overlap={chunk_overlap}")

    def process_slides(self, slides_data: List[Dict]) -> List[Document]:
        """
        Process PPT slides into documents.

        Args:
            slides_data: List of slide dictionaries with texts, tables, etc.

        Returns:
            List of Document objects ready for embedding
        """
        documents = []

        for slide in slides_data:
            slide_num = slide.get("slide_num", 0)
            slide_title = self._extract_title(slide)

            # Process text content
            texts = slide.get("texts", [])
            if texts:
                combined_text = "\n".join(texts)
                chunks = self.chunk_text(
                    combined_text,
                    {
                        "slide_num": slide_num,
                        "slide_title": slide_title,
                        "content_type": "text",
                        "has_table": False,
                        "has_image": False
                    }
                )
                documents.extend(chunks)

            # Process tables
            tables = slide.get("tables", [])
            for i, table in enumerate(tables):
                table_text = self._format_table(table)
                if table_text:
                    chunks = self.chunk_text(
                        table_text,
                        {
                            "slide_num": slide_num,
                            "slide_title": slide_title,
                            "content_type": "table",
                            "table_index": i,
                            "has_table": True,
                            "has_image": False
                        }
                    )
                    documents.extend(chunks)

            # Process vision analysis (image descriptions)
            vision_analysis = slide.get("vision_analysis", "")
            if vision_analysis:
                chunks = self.chunk_text(
                    vision_analysis,
                    {
                        "slide_num": slide_num,
                        "slide_title": slide_title,
                        "content_type": "image_description",
                        "has_table": False,
                        "has_image": True
                    }
                )
                documents.extend(chunks)

        logger.info(f"Processed {len(slides_data)} slides into {len(documents)} documents")
        return documents

    def chunk_text(self, text: str, metadata: Dict) -> List[Document]:
        """
        Split text into chunks with metadata.

        Args:
            text: Text to split into chunks
            metadata: Base metadata to attach to each chunk

        Returns:
            List of Document objects
        """
        if not text.strip():
            return []

        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        documents = []

        for i, chunk in enumerate(chunks):
            # Create chunk-specific metadata
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_id"] = self._generate_chunk_id(chunk)
            chunk_metadata["chunk_size"] = len(chunk)
            chunk_metadata["total_chunks"] = len(chunks)

            documents.append(Document(
                content=chunk,
                metadata=chunk_metadata
            ))

        return documents

    def _extract_title(self, slide: Dict) -> str:
        """
        Extract title from slide content.

        Args:
            slide: Slide dictionary

        Returns:
            Extracted title or empty string
        """
        texts = slide.get("texts", [])
        if texts:
            # Assume first text is title if it's short enough
            first_text = texts[0]
            if len(first_text) < 100:
                return first_text
        return ""

    def _format_table(self, table: List[List[str]]) -> str:
        """
        Format table data as text.

        Args:
            table: 2D list representing table data

        Returns:
            Formatted table as string
        """
        if not table:
            return ""

        formatted_rows = []
        for row in table:
            if row:  # Skip empty rows
                formatted_rows.append(" | ".join(str(cell) for cell in row))

        return "\n".join(formatted_rows)

    def _generate_chunk_id(self, text: str) -> str:
        """
        Generate unique ID for chunk.

        Args:
            text: Chunk text

        Returns:
            Unique chunk ID
        """
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def merge_documents(self, documents: List[Document], max_size: int = 1000) -> List[Document]:
        """
        Merge small documents to optimize for retrieval.

        Args:
            documents: List of documents to merge
            max_size: Maximum size of merged document

        Returns:
            List of merged documents
        """
        if not documents:
            return []

        merged = []
        current_doc = None
        current_size = 0

        for doc in documents:
            doc_size = len(doc.content)

            # Check if we should start a new merged document
            if current_doc is None or current_size + doc_size > max_size:
                if current_doc:
                    merged.append(current_doc)
                current_doc = Document(
                    content=doc.content,
                    metadata=doc.metadata.copy()
                )
                current_size = doc_size
            else:
                # Merge with current document
                current_doc.content += "\n\n" + doc.content
                current_size += doc_size + 2  # Account for \n\n

                # Update metadata for merged document
                if current_doc.metadata.get("slide_num") != doc.metadata.get("slide_num"):
                    # Merged across slides
                    current_doc.metadata["content_type"] = "merged"
                    if "chunk_index" in current_doc.metadata:
                        del current_doc.metadata["chunk_index"]

        # Add the last document
        if current_doc:
            merged.append(current_doc)

        logger.info(f"Merged {len(documents)} documents into {len(merged)} documents")
        return merged

    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        Extract keywords from text for hybrid search.

        Args:
            text: Input text
            top_k: Number of keywords to extract

        Returns:
            List of keywords
        """
        # Simple keyword extraction (can be improved with NLTK or spaCy)
        import re
        from collections import Counter

        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z가-힣]{3,}\b', text.lower())

        # Count frequencies
        word_freq = Counter(words)

        # Filter common stop words (basic Korean and English)
        stop_words = {
            '이', '그', '저', '것', '수', '등', '및', '의', '를', '을', '가', '에',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
        }
        keywords = [word for word, _ in word_freq.most_common(top_k * 2)
                   if word not in stop_words][:top_k]

        return keywords

    def get_statistics(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Get statistics about processed documents.

        Args:
            documents: List of documents

        Returns:
            Statistics dictionary
        """
        if not documents:
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "slides_processed": 0
            }

        chunk_sizes = [len(doc.content) for doc in documents]
        slide_nums = set(doc.metadata.get("slide_num", 0) for doc in documents)

        return {
            "total_documents": len(documents),
            "total_chunks": len([d for d in documents if "chunk_index" in d.metadata]),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
            "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
            "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0,
            "slides_processed": len(slide_nums),
            "content_types": list(set(d.metadata.get("content_type", "unknown") for d in documents))
        }