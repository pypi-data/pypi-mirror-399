"""
Reranking module for Production RAG.

Improves retrieval quality by reranking initial results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .types import Chunk, RetrievalResult


@dataclass
class RerankerConfig:
    """Configuration for reranker."""
    
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    batch_size: int = 32
    top_k: Optional[int] = None  # None = return all
    score_threshold: float = 0.0
    device: str = "cpu"
    normalize_scores: bool = True


class BaseReranker(ABC):
    """Abstract base class for rerankers."""
    
    @abstractmethod
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Rerank retrieval results."""
        pass


class CrossEncoderReranker(BaseReranker):
    """
    Reranker using cross-encoder models.
    
    Cross-encoders jointly encode query and document for
    more accurate relevance scoring.
    """
    
    def __init__(self, config: Optional[RerankerConfig] = None):
        self.config = config or RerankerConfig()
        self._model = None
    
    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(
                    self.config.model_name,
                    device=self.config.device
                )
            except ImportError:
                raise ImportError(
                    "sentence-transformers required. Install with: "
                    "pip install sentence-transformers"
                )
    
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Rerank results using cross-encoder."""
        if not results:
            return []
        
        self._load_model()
        
        # Prepare pairs for scoring
        pairs = [(query, r.chunk.content) for r in results]
        
        # Score all pairs
        scores = self._model.predict(
            pairs,
            batch_size=self.config.batch_size,
            show_progress_bar=False
        )
        
        # Normalize scores if requested
        if self.config.normalize_scores:
            scores = self._sigmoid(scores)
        
        # Update results with new scores
        reranked = []
        for result, score in zip(results, scores):
            if score >= self.config.score_threshold:
                reranked.append(RetrievalResult(
                    chunk=result.chunk,
                    score=float(score),
                    metadata={
                        **result.metadata,
                        "original_score": result.score,
                        "reranked": True
                    }
                ))
        
        # Sort by new scores
        reranked.sort(key=lambda x: x.score, reverse=True)
        
        # Apply top_k
        k = top_k or self.config.top_k
        if k:
            reranked = reranked[:k]
        
        return reranked
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Apply sigmoid normalization."""
        return 1 / (1 + np.exp(-x))


class CohereReranker(BaseReranker):
    """Reranker using Cohere Rerank API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "rerank-english-v3.0",
        top_k: Optional[int] = None
    ):
        self.api_key = api_key
        self.model = model
        self.top_k = top_k
        self._client = None
    
    def _get_client(self):
        """Get or create Cohere client."""
        if self._client is None:
            try:
                import cohere
                self._client = cohere.Client(self.api_key)
            except ImportError:
                raise ImportError(
                    "cohere required. Install with: pip install cohere"
                )
        return self._client
    
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Rerank using Cohere API."""
        if not results:
            return []
        
        client = self._get_client()
        k = top_k or self.top_k or len(results)
        
        documents = [r.chunk.content for r in results]
        
        response = client.rerank(
            query=query,
            documents=documents,
            model=self.model,
            top_n=k
        )
        
        reranked = []
        for item in response.results:
            original = results[item.index]
            reranked.append(RetrievalResult(
                chunk=original.chunk,
                score=item.relevance_score,
                metadata={
                    **original.metadata,
                    "original_score": original.score,
                    "original_index": item.index,
                    "reranked": True
                }
            ))
        
        return reranked


class LLMReranker(BaseReranker):
    """
    Reranker using LLM for relevance scoring.
    
    Useful for complex queries requiring reasoning.
    """
    
    DEFAULT_PROMPT = """Given the following query and document, rate the relevance of the document to the query on a scale of 0-10.

Query: {query}

Document: {document}

Respond with only a number from 0-10."""
    
    def __init__(
        self,
        llm_fn: Callable[[str], str],
        prompt_template: Optional[str] = None,
        top_k: Optional[int] = None,
        batch_size: int = 5
    ):
        """
        Args:
            llm_fn: Function that takes prompt and returns LLM response
            prompt_template: Custom prompt with {query} and {document} placeholders
            top_k: Number of results to return
            batch_size: Number of parallel LLM calls
        """
        self.llm_fn = llm_fn
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT
        self.top_k = top_k
        self.batch_size = batch_size
    
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Rerank using LLM scoring."""
        if not results:
            return []
        
        scored_results = []
        
        for result in results:
            prompt = self.prompt_template.format(
                query=query,
                document=result.chunk.content[:2000]  # Truncate long docs
            )
            
            try:
                response = self.llm_fn(prompt)
                score = self._parse_score(response)
            except Exception:
                score = 0.0
            
            scored_results.append(RetrievalResult(
                chunk=result.chunk,
                score=score / 10.0,  # Normalize to 0-1
                metadata={
                    **result.metadata,
                    "original_score": result.score,
                    "reranked": True,
                    "reranker": "llm"
                }
            ))
        
        # Sort by score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        
        k = top_k or self.top_k
        if k:
            scored_results = scored_results[:k]
        
        return scored_results
    
    def _parse_score(self, response: str) -> float:
        """Parse score from LLM response."""
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        if numbers:
            score = float(numbers[0])
            return min(max(score, 0), 10)  # Clamp to 0-10
        return 0.0


class RRFReranker(BaseReranker):
    """
    Reciprocal Rank Fusion reranker.
    
    Combines multiple result lists using RRF algorithm.
    """
    
    def __init__(self, k: int = 60):
        """
        Args:
            k: RRF constant (default 60)
        """
        self.k = k
    
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Single list reranking (pass-through with RRF scores)."""
        if not results:
            return []
        
        reranked = []
        for rank, result in enumerate(results):
            rrf_score = 1.0 / (self.k + rank + 1)
            reranked.append(RetrievalResult(
                chunk=result.chunk,
                score=rrf_score,
                metadata={
                    **result.metadata,
                    "original_score": result.score,
                    "rrf_rank": rank + 1
                }
            ))
        
        if top_k:
            reranked = reranked[:top_k]
        
        return reranked
    
    def fuse(
        self,
        result_lists: List[List[RetrievalResult]],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Fuse multiple result lists using RRF.
        
        Args:
            result_lists: List of result lists to fuse
            top_k: Number of results to return
        
        Returns:
            Fused and reranked results
        """
        # Calculate RRF scores
        chunk_scores: Dict[str, Tuple[Chunk, float, dict]] = {}
        
        for results in result_lists:
            for rank, result in enumerate(results):
                chunk_id = result.chunk.id
                rrf_score = 1.0 / (self.k + rank + 1)
                
                if chunk_id in chunk_scores:
                    _, current_score, metadata = chunk_scores[chunk_id]
                    chunk_scores[chunk_id] = (
                        result.chunk,
                        current_score + rrf_score,
                        metadata
                    )
                else:
                    chunk_scores[chunk_id] = (
                        result.chunk,
                        rrf_score,
                        result.metadata
                    )
        
        # Create fused results
        fused = [
            RetrievalResult(
                chunk=chunk,
                score=score,
                metadata={**metadata, "rrf_fused": True}
            )
            for chunk, score, metadata in chunk_scores.values()
        ]
        
        # Sort by fused score
        fused.sort(key=lambda x: x.score, reverse=True)
        
        if top_k:
            fused = fused[:top_k]
        
        return fused


class EnsembleReranker(BaseReranker):
    """
    Ensemble of multiple rerankers with weighted scoring.
    
    Example:
        ensemble = EnsembleReranker([
            (CrossEncoderReranker(), 0.7),
            (RRFReranker(), 0.3)
        ])
    """
    
    def __init__(
        self,
        rerankers: List[Tuple[BaseReranker, float]],
        aggregation: str = "weighted_sum"  # weighted_sum, max, min
    ):
        self.rerankers = rerankers
        self.aggregation = aggregation
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1."""
        total = sum(w for _, w in self.rerankers)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Rerank using ensemble of rerankers."""
        if not results:
            return []
        
        # Get scores from each reranker
        all_scores: Dict[str, List[Tuple[float, float]]] = {}  # chunk_id -> [(score, weight)]
        chunk_map: Dict[str, Chunk] = {}
        
        for reranker, weight in self.rerankers:
            reranked = reranker.rerank(query, results)
            
            for result in reranked:
                chunk_id = result.chunk.id
                chunk_map[chunk_id] = result.chunk
                
                if chunk_id not in all_scores:
                    all_scores[chunk_id] = []
                all_scores[chunk_id].append((result.score, weight))
        
        # Aggregate scores
        final_results = []
        for chunk_id, scores_weights in all_scores.items():
            if self.aggregation == "weighted_sum":
                final_score = sum(s * w for s, w in scores_weights)
            elif self.aggregation == "max":
                final_score = max(s for s, _ in scores_weights)
            elif self.aggregation == "min":
                final_score = min(s for s, _ in scores_weights)
            else:
                final_score = sum(s * w for s, w in scores_weights)
            
            final_results.append(RetrievalResult(
                chunk=chunk_map[chunk_id],
                score=final_score,
                metadata={"ensemble_reranked": True}
            ))
        
        # Sort by final score
        final_results.sort(key=lambda x: x.score, reverse=True)
        
        if top_k:
            final_results = final_results[:top_k]
        
        return final_results


def get_reranker(
    provider: str = "cross-encoder",
    **kwargs
) -> BaseReranker:
    """
    Factory function to get reranker by provider name.
    
    Args:
        provider: One of 'cross-encoder', 'cohere', 'rrf'
        **kwargs: Provider-specific arguments
    
    Returns:
        BaseReranker instance
    """
    providers = {
        "cross-encoder": CrossEncoderReranker,
        "cohere": CohereReranker,
        "rrf": RRFReranker,
    }
    
    if provider not in providers:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available: {list(providers.keys())}"
        )
    
    return providers[provider](**kwargs)
