"""
Type definitions for Production RAG.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum, auto
import hashlib


class DocumentType(Enum):
    """Supported document types."""
    TEXT = auto()
    PDF = auto()
    HTML = auto()
    MARKDOWN = auto()
    JSON = auto()
    CSV = auto()
    DOCX = auto()


class ChunkingStrategy(Enum):
    """Chunking strategies."""
    FIXED_SIZE = auto()
    SENTENCE = auto()
    PARAGRAPH = auto()
    SEMANTIC = auto()
    RECURSIVE = auto()
    CUSTOM = auto()


@dataclass
class Document:
    """
    Represents a document in the RAG system.
    
    Attributes:
        content: Raw document content
        metadata: Document metadata
        doc_id: Unique document identifier
        doc_type: Type of document
        source: Source path or URL
    """
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: Optional[str] = None
    doc_type: DocumentType = DocumentType.TEXT
    source: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.doc_id is None:
            self.doc_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique document ID."""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:12]
        return f"doc_{content_hash}"
    
    def __len__(self) -> int:
        return len(self.content)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_type": self.doc_type.name,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Chunk:
    """
    Represents a chunk of a document.
    
    Attributes:
        content: Chunk text content
        doc_id: Parent document ID
        chunk_id: Unique chunk identifier
        chunk_index: Position in document
        embedding: Vector embedding
        metadata: Chunk metadata
    """
    content: str
    doc_id: str
    chunk_id: Optional[str] = None
    chunk_index: int = 0
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0
    
    def __post_init__(self):
        if self.chunk_id is None:
            self.chunk_id = f"{self.doc_id}_chunk_{self.chunk_index}"
    
    def __len__(self) -> int:
        return len(self.content)
    
    @property
    def has_embedding(self) -> bool:
        return self.embedding is not None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "has_embedding": self.has_embedding,
        }


@dataclass
class Query:
    """
    Represents a user query.
    
    Attributes:
        text: Query text
        query_id: Unique query identifier
        filters: Metadata filters
        top_k: Number of results to retrieve
        embedding: Query embedding
    """
    text: str
    query_id: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    top_k: int = 5
    embedding: Optional[List[float]] = None
    rerank: bool = True
    include_metadata: bool = True
    
    def __post_init__(self):
        if self.query_id is None:
            self.query_id = f"query_{hashlib.md5(self.text.encode()).hexdigest()[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "text": self.text,
            "filters": self.filters,
            "top_k": self.top_k,
            "rerank": self.rerank,
        }


@dataclass
class RetrievalResult:
    """
    Result from retrieval operation.
    
    Attributes:
        chunks: Retrieved chunks
        scores: Similarity scores
        query: Original query
    """
    chunks: List[Chunk]
    scores: List[float]
    query: Query
    retrieval_time_ms: float = 0.0
    reranked: bool = False
    
    def __len__(self) -> int:
        return len(self.chunks)
    
    def __iter__(self):
        return iter(zip(self.chunks, self.scores))
    
    @property
    def top_chunk(self) -> Optional[Chunk]:
        return self.chunks[0] if self.chunks else None
    
    @property
    def top_score(self) -> float:
        return self.scores[0] if self.scores else 0.0
    
    def get_context(self, max_chunks: int = 5, separator: str = "\n\n") -> str:
        """Get combined context from top chunks."""
        return separator.join(c.content for c in self.chunks[:max_chunks])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query.to_dict(),
            "num_results": len(self.chunks),
            "chunks": [c.to_dict() for c in self.chunks],
            "scores": self.scores,
            "retrieval_time_ms": self.retrieval_time_ms,
            "reranked": self.reranked,
        }


@dataclass
class Response:
    """
    Complete RAG response.
    
    Attributes:
        answer: Generated answer
        sources: Source chunks used
        query: Original query
        confidence: Answer confidence
    """
    answer: str
    sources: List[Chunk]
    query: Query
    confidence: float = 0.0
    retrieval_result: Optional[RetrievalResult] = None
    generation_time_ms: float = 0.0
    total_time_ms: float = 0.0
    model_used: str = ""
    tokens_used: int = 0
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "query": self.query.to_dict(),
            "sources": [s.to_dict() for s in self.sources],
            "confidence": self.confidence,
            "generation_time_ms": self.generation_time_ms,
            "total_time_ms": self.total_time_ms,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "cached": self.cached,
        }
    
    def __str__(self) -> str:
        return self.answer


@dataclass
class PipelineMetrics:
    """Metrics for pipeline performance."""
    total_queries: int = 0
    avg_retrieval_time_ms: float = 0.0
    avg_generation_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    avg_chunks_retrieved: float = 0.0
    error_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_queries": self.total_queries,
            "avg_retrieval_time_ms": self.avg_retrieval_time_ms,
            "avg_generation_time_ms": self.avg_generation_time_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "avg_chunks_retrieved": self.avg_chunks_retrieved,
            "error_rate": self.error_rate,
        }
