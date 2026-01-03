"""
Embedding generation for Production RAG.

Supports multiple embedding backends with automatic fallback.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
import numpy as np


@dataclass
class EmbedderConfig:
    """Configuration for embedder."""
    
    model_name: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize: bool = True
    cache_embeddings: bool = True
    cache_dir: Optional[str] = None
    device: str = "cpu"
    show_progress: bool = False
    max_length: int = 512
    pooling_strategy: str = "mean"  # mean, cls, max


class BaseEmbedder(ABC):
    """Abstract base class for embedders."""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass


class SentenceTransformerEmbedder(BaseEmbedder):
    """Embedder using sentence-transformers library."""
    
    def __init__(self, config: Optional[EmbedderConfig] = None):
        self.config = config or EmbedderConfig()
        self._model = None
        self._dimension = None
        self._cache: Dict[str, np.ndarray] = {}
        
        if self.config.cache_dir:
            self._cache_path = Path(self.config.cache_dir)
            self._cache_path.mkdir(parents=True, exist_ok=True)
            self._load_cache()
    
    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(
                    self.config.model_name,
                    device=self.config.device
                )
                self._dimension = self._model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers required. Install with: "
                    "pip install sentence-transformers"
                )
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(
            f"{self.config.model_name}:{text}".encode()
        ).hexdigest()
    
    def _load_cache(self):
        """Load cache from disk."""
        cache_file = self._cache_path / "embeddings_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    self._cache = {k: np.array(v) for k, v in data.items()}
            except Exception:
                self._cache = {}
    
    def _save_cache(self):
        """Save cache to disk."""
        if self.config.cache_dir:
            cache_file = self._cache_path / "embeddings_cache.json"
            with open(cache_file, "w") as f:
                json.dump(
                    {k: v.tolist() for k, v in self._cache.items()},
                    f
                )
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        self._load_model()
        
        # Check cache
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        for i, text in enumerate(texts):
            if self.config.cache_embeddings:
                key = self._get_cache_key(text)
                if key in self._cache:
                    embeddings.append((i, self._cache[key]))
                    continue
            
            texts_to_embed.append(text)
            indices_to_embed.append(i)
        
        # Embed uncached texts
        if texts_to_embed:
            new_embeddings = self._model.encode(
                texts_to_embed,
                batch_size=self.config.batch_size,
                show_progress_bar=self.config.show_progress,
                normalize_embeddings=self.config.normalize,
                convert_to_numpy=True
            )
            
            for idx, text, emb in zip(indices_to_embed, texts_to_embed, new_embeddings):
                if self.config.cache_embeddings:
                    key = self._get_cache_key(text)
                    self._cache[key] = emb
                embeddings.append((idx, emb))
            
            if self.config.cache_embeddings and self.config.cache_dir:
                self._save_cache()
        
        # Sort by original index and return
        embeddings.sort(key=lambda x: x[0])
        return np.array([e[1] for e in embeddings])
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        return self.embed([query])[0]
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        self._load_model()
        return self._dimension


class OpenAIEmbedder(BaseEmbedder):
    """Embedder using OpenAI API."""
    
    DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        batch_size: int = 100,
        dimensions: Optional[int] = None
    ):
        self.api_key = api_key
        self.model = model
        self.batch_size = batch_size
        self._dimensions = dimensions or self.DIMENSIONS.get(model, 1536)
        self._client = None
    
    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "openai required. Install with: pip install openai"
                )
        return self._client
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI API."""
        client = self._get_client()
        
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = client.embeddings.create(
                model=self.model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return np.array(all_embeddings)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        return self.embed([query])[0]
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimensions


class CohereEmbedder(BaseEmbedder):
    """Embedder using Cohere API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "embed-english-v3.0",
        input_type: str = "search_document"
    ):
        self.api_key = api_key
        self.model = model
        self.input_type = input_type
        self._client = None
        self._dimension = 1024  # Default for v3 models
    
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
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Cohere API."""
        client = self._get_client()
        
        response = client.embed(
            texts=texts,
            model=self.model,
            input_type=self.input_type
        )
        
        return np.array(response.embeddings)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        # Use search_query input type for queries
        client = self._get_client()
        response = client.embed(
            texts=[query],
            model=self.model,
            input_type="search_query"
        )
        return np.array(response.embeddings[0])
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension


class SimpleEmbedder(BaseEmbedder):
    """
    Simple TF-IDF based embedder for testing/fallback.
    
    No external dependencies required.
    """
    
    def __init__(self, dimension: int = 384, vocab_size: int = 10000):
        self._dimension = dimension
        self.vocab_size = vocab_size
        self._vocab: Dict[str, int] = {}
        self._idf: Dict[str, float] = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        import re
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _hash_token(self, token: str) -> int:
        """Hash token to index."""
        return hash(token) % self._dimension
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate simple hash-based embeddings."""
        embeddings = []
        
        for text in texts:
            tokens = self._tokenize(text)
            embedding = np.zeros(self._dimension)
            
            for token in tokens:
                idx = self._hash_token(token)
                embedding[idx] += 1
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        return self.embed([query])[0]
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension


class HybridEmbedder(BaseEmbedder):
    """
    Combines multiple embedders with weighted fusion.
    
    Example:
        embedder = HybridEmbedder([
            (SentenceTransformerEmbedder(), 0.7),
            (SimpleEmbedder(), 0.3)
        ])
    """
    
    def __init__(self, embedders: List[tuple[BaseEmbedder, float]]):
        self.embedders = embedders
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1."""
        total = sum(w for _, w in self.embedders)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate hybrid embeddings."""
        all_embeddings = []
        
        for embedder, weight in self.embedders:
            emb = embedder.embed(texts) * weight
            all_embeddings.append(emb)
        
        # Concatenate all embeddings
        return np.concatenate(all_embeddings, axis=1)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        return self.embed([query])[0]
    
    @property
    def dimension(self) -> int:
        """Return total embedding dimension."""
        return sum(e.dimension for e, _ in self.embedders)


def get_embedder(
    provider: str = "sentence-transformers",
    **kwargs
) -> BaseEmbedder:
    """
    Factory function to get embedder by provider name.
    
    Args:
        provider: One of 'sentence-transformers', 'openai', 'cohere', 'simple'
        **kwargs: Provider-specific arguments
    
    Returns:
        BaseEmbedder instance
    
    Example:
        embedder = get_embedder("openai", api_key="sk-...")
    """
    providers = {
        "sentence-transformers": SentenceTransformerEmbedder,
        "openai": OpenAIEmbedder,
        "cohere": CohereEmbedder,
        "simple": SimpleEmbedder,
    }
    
    if provider not in providers:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available: {list(providers.keys())}"
        )
    
    return providers[provider](**kwargs)
