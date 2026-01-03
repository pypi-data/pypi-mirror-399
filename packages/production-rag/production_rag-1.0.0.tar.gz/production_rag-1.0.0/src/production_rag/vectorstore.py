"""
Vector Store - Efficient vector storage and retrieval.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import pickle

from .types import Chunk

logger = logging.getLogger(__name__)


@dataclass
class VectorStoreConfig:
    """Configuration for Vector Store."""
    embedding_dim: int = 384
    index_type: str = "flat"  # flat, hnsw, ivf
    metric: str = "cosine"    # cosine, euclidean, dot
    ef_construction: int = 200
    ef_search: int = 50
    nlist: int = 100


class VectorStore:
    """
    High-performance vector storage.
    
    Supports multiple backends and index types for
    efficient similarity search at scale.
    
    Examples:
        >>> store = VectorStore(embedding_dim=384)
        >>> store.add(chunks)
        >>> results = store.search(query_embedding, top_k=5)
    """
    
    def __init__(
        self,
        embedding_dim: int = 384,
        config: Optional[VectorStoreConfig] = None,
    ):
        """
        Initialize vector store.
        
        Args:
            embedding_dim: Dimension of embeddings
            config: Store configuration
        """
        self.config = config or VectorStoreConfig(embedding_dim=embedding_dim)
        self.embedding_dim = self.config.embedding_dim
        
        # Storage
        self._chunks: Dict[str, Chunk] = {}
        self._embeddings: List[List[float]] = []
        self._chunk_ids: List[str] = []
        self._index = None
        
        self._init_index()
    
    def _init_index(self) -> None:
        """Initialize the vector index."""
        try:
            import numpy as np
            self._np = np
            self._use_numpy = True
        except ImportError:
            self._use_numpy = False
            logger.warning("NumPy not available. Using pure Python.")
    
    def add(self, chunks: List[Chunk]) -> None:
        """
        Add chunks to the store.
        
        Args:
            chunks: Chunks with embeddings
        """
        for chunk in chunks:
            if not chunk.has_embedding:
                logger.warning(f"Chunk {chunk.chunk_id} has no embedding, skipping")
                continue
            
            self._chunks[chunk.chunk_id] = chunk
            self._embeddings.append(chunk.embedding)
            self._chunk_ids.append(chunk.chunk_id)
        
        logger.debug(f"Added {len(chunks)} chunks to store")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Chunk, float]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            filters: Metadata filters
        
        Returns:
            List of (chunk, score) tuples
        """
        if not self._embeddings:
            return []
        
        # Calculate similarities
        if self._use_numpy:
            scores = self._cosine_similarity_numpy(query_embedding)
        else:
            scores = self._cosine_similarity_python(query_embedding)
        
        # Sort by score
        indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        results = []
        for idx in indices:
            if len(results) >= top_k:
                break
            
            chunk_id = self._chunk_ids[idx]
            chunk = self._chunks[chunk_id]
            
            # Apply filters
            if filters and not self._matches_filters(chunk, filters):
                continue
            
            results.append((chunk, scores[idx]))
        
        return results
    
    def _cosine_similarity_numpy(self, query: List[float]) -> List[float]:
        """Compute cosine similarity using NumPy."""
        query_arr = self._np.array(query)
        embeddings_arr = self._np.array(self._embeddings)
        
        # Normalize
        query_norm = query_arr / (self._np.linalg.norm(query_arr) + 1e-8)
        embeddings_norm = embeddings_arr / (
            self._np.linalg.norm(embeddings_arr, axis=1, keepdims=True) + 1e-8
        )
        
        similarities = self._np.dot(embeddings_norm, query_norm)
        return similarities.tolist()
    
    def _cosine_similarity_python(self, query: List[float]) -> List[float]:
        """Compute cosine similarity in pure Python."""
        def cosine_sim(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = sum(a * a for a in v1) ** 0.5
            norm2 = sum(b * b for b in v2) ** 0.5
            return dot / (norm1 * norm2 + 1e-8)
        
        return [cosine_sim(query, emb) for emb in self._embeddings]
    
    def _matches_filters(self, chunk: Chunk, filters: Dict[str, Any]) -> bool:
        """Check if chunk matches filters."""
        for key, value in filters.items():
            if key not in chunk.metadata:
                return False
            if chunk.metadata[key] != value:
                return False
        return True
    
    def get(self, chunk_id: str) -> Optional[Chunk]:
        """Get chunk by ID."""
        return self._chunks.get(chunk_id)
    
    def delete(self, doc_id: str) -> bool:
        """Delete all chunks for a document."""
        to_delete = [
            cid for cid, chunk in self._chunks.items()
            if chunk.doc_id == doc_id
        ]
        
        for chunk_id in to_delete:
            idx = self._chunk_ids.index(chunk_id)
            del self._chunks[chunk_id]
            del self._embeddings[idx]
            del self._chunk_ids[idx]
        
        return len(to_delete) > 0
    
    def clear(self) -> None:
        """Clear all data."""
        self._chunks.clear()
        self._embeddings.clear()
        self._chunk_ids.clear()
    
    def count(self) -> int:
        """Get total chunk count."""
        return len(self._chunks)
    
    def save(self, path: Path) -> None:
        """Save store to disk."""
        path.mkdir(parents=True, exist_ok=True)
        
        # Save chunks
        with open(path / "chunks.pkl", "wb") as f:
            pickle.dump(self._chunks, f)
        
        # Save embeddings and IDs
        with open(path / "embeddings.pkl", "wb") as f:
            pickle.dump({
                "embeddings": self._embeddings,
                "chunk_ids": self._chunk_ids,
            }, f)
    
    def load(self, path: Path) -> None:
        """Load store from disk."""
        with open(path / "chunks.pkl", "rb") as f:
            self._chunks = pickle.load(f)
        
        with open(path / "embeddings.pkl", "rb") as f:
            data = pickle.load(f)
            self._embeddings = data["embeddings"]
            self._chunk_ids = data["chunk_ids"]
