"""
Retriever - Handles document retrieval.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .types import Query, Chunk, RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class RetrieverConfig:
    """Configuration for Retriever."""
    top_k: int = 5
    similarity_threshold: float = 0.0
    max_tokens: int = 4000
    diversity_factor: float = 0.0


class Retriever:
    """
    Document Retriever.
    
    Handles query embedding and vector search for
    retrieving relevant chunks.
    
    Examples:
        >>> retriever = Retriever(vector_store, embedder)
        >>> results = retriever.retrieve(query)
    """
    
    def __init__(
        self,
        vector_store,
        embedder,
        config: Optional[RetrieverConfig] = None,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.config = config or RetrieverConfig()
    
    def retrieve(self, query: Query) -> RetrievalResult:
        """
        Retrieve relevant chunks for query.
        
        Args:
            query: Query object
        
        Returns:
            RetrievalResult with chunks and scores
        """
        start_time = time.time()
        
        # Embed query
        query.embedding = self.embedder.embed(query.text)
        
        # Search
        results = self.vector_store.search(
            query_embedding=query.embedding,
            top_k=query.top_k,
            filters=query.filters,
        )
        
        # Filter by threshold
        chunks = []
        scores = []
        for chunk, score in results:
            if score >= self.config.similarity_threshold:
                chunks.append(chunk)
                scores.append(score)
        
        retrieval_time = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            chunks=chunks,
            scores=scores,
            query=query,
            retrieval_time_ms=retrieval_time,
        )
    
    def hybrid_retrieve(
        self,
        query: Query,
        keyword_weight: float = 0.3,
    ) -> RetrievalResult:
        """
        Hybrid retrieval combining vector and keyword search.
        
        Args:
            query: Query object
            keyword_weight: Weight for keyword scores
        
        Returns:
            RetrievalResult with merged results
        """
        # Vector search
        vector_result = self.retrieve(query)
        
        # Could add keyword search here and merge
        # For now, return vector results
        return vector_result
