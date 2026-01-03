"""
Caching module for Production RAG.

Provides caching for embeddings, retrieval results, and generated responses.
"""

from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
import threading


T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Single cache entry with metadata."""
    
    key: str
    value: T
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    ttl: Optional[float] = None  # Time to live in seconds
    access_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access time and count."""
        self.accessed_at = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics."""
    
    hits: int = 0
    misses: int = 0
    size: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class BaseCache(ABC):
    """Abstract base class for caches."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass
    
    @abstractmethod
    def clear(self):
        """Clear all entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class MemoryCache(BaseCache):
    """
    In-memory LRU cache with TTL support.
    
    Thread-safe implementation suitable for single-process applications.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[float] = None
    ):
        """
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats.misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._stats.misses += 1
                return None
            
            entry.touch()
            self._stats.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache with optional TTL."""
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.default_ttl
            )
            self._stats.size = len(self._cache)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False
    
    def clear(self):
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            self._stats.size = len(self._cache)
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                size=self._stats.size,
                evictions=self._stats.evictions
            )
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].accessed_at
        )
        
        del self._cache[lru_key]
        self._stats.evictions += 1


class DiskCache(BaseCache):
    """
    Disk-based cache for persistence across restarts.
    
    Uses JSON serialization for simple types.
    """
    
    def __init__(
        self,
        cache_dir: Union[str, Path],
        max_size_mb: int = 100,
        default_ttl: Optional[float] = None
    ):
        """
        Args:
            cache_dir: Directory for cache files
            max_size_mb: Maximum cache size in MB
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self._stats = CacheStats()
        self._lock = threading.RLock()
        
        # Index file for metadata
        self._index_file = self.cache_dir / "_index.json"
        self._index: Dict[str, dict] = self._load_index()
    
    def _load_index(self) -> Dict[str, dict]:
        """Load index from disk."""
        if self._index_file.exists():
            try:
                with open(self._index_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_index(self):
        """Save index to disk."""
        with open(self._index_file, "w") as f:
            json.dump(self._index, f)
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._index:
                self._stats.misses += 1
                return None
            
            metadata = self._index[key]
            
            # Check TTL
            if metadata.get("ttl"):
                created = metadata["created_at"]
                if time.time() - created > metadata["ttl"]:
                    self.delete(key)
                    self._stats.misses += 1
                    return None
            
            # Read file
            file_path = self._get_file_path(key)
            if not file_path.exists():
                del self._index[key]
                self._save_index()
                self._stats.misses += 1
                return None
            
            try:
                with open(file_path, "r") as f:
                    value = json.load(f)
                
                # Update access time
                self._index[key]["accessed_at"] = time.time()
                self._index[key]["access_count"] = \
                    self._index[key].get("access_count", 0) + 1
                self._save_index()
                
                self._stats.hits += 1
                return value
            except Exception:
                self._stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        with self._lock:
            # Check size and evict if needed
            self._ensure_capacity()
            
            file_path = self._get_file_path(key)
            
            try:
                with open(file_path, "w") as f:
                    json.dump(value, f)
                
                self._index[key] = {
                    "created_at": time.time(),
                    "accessed_at": time.time(),
                    "ttl": ttl or self.default_ttl,
                    "access_count": 0,
                    "size": file_path.stat().st_size
                }
                self._save_index()
            except Exception as e:
                raise RuntimeError(f"Failed to cache value: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key not in self._index:
                return False
            
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
            
            del self._index[key]
            self._save_index()
            return True
    
    def clear(self):
        """Clear all entries."""
        with self._lock:
            for key in list(self._index.keys()):
                file_path = self._get_file_path(key)
                if file_path.exists():
                    file_path.unlink()
            
            self._index.clear()
            self._save_index()
            self._stats = CacheStats()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                size=len(self._index),
                evictions=self._stats.evictions
            )
    
    def _ensure_capacity(self):
        """Ensure cache is under size limit."""
        total_size = sum(
            meta.get("size", 0) for meta in self._index.values()
        )
        
        while total_size > self.max_size_bytes and self._index:
            # Find LRU entry
            lru_key = min(
                self._index.keys(),
                key=lambda k: self._index[k].get("accessed_at", 0)
            )
            
            total_size -= self._index[lru_key].get("size", 0)
            self.delete(lru_key)
            self._stats.evictions += 1


class RedisCache(BaseCache):
    """
    Redis-based cache for distributed applications.
    
    Requires redis-py package.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "rag:",
        default_ttl: Optional[float] = None
    ):
        """
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            prefix: Key prefix for namespacing
            default_ttl: Default TTL in seconds
        """
        self.prefix = prefix
        self.default_ttl = default_ttl
        self._stats = CacheStats()
        
        try:
            import redis
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
        except ImportError:
            raise ImportError(
                "redis required. Install with: pip install redis"
            )
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        redis_key = self._make_key(key)
        value = self._client.get(redis_key)
        
        if value is None:
            self._stats.misses += 1
            return None
        
        self._stats.hits += 1
        return json.loads(value)
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in Redis."""
        redis_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        if ttl:
            self._client.setex(
                redis_key,
                int(ttl),
                json.dumps(value)
            )
        else:
            self._client.set(redis_key, json.dumps(value))
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        redis_key = self._make_key(key)
        return bool(self._client.delete(redis_key))
    
    def clear(self):
        """Clear all entries with prefix."""
        pattern = f"{self.prefix}*"
        keys = self._client.keys(pattern)
        if keys:
            self._client.delete(*keys)
        self._stats = CacheStats()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pattern = f"{self.prefix}*"
        size = len(self._client.keys(pattern))
        return CacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            size=size,
            evictions=self._stats.evictions
        )


class SemanticCache(BaseCache):
    """
    Semantic cache that finds similar queries.
    
    Uses embeddings to match semantically similar queries
    to cached responses.
    """
    
    def __init__(
        self,
        embedder: Any,  # BaseEmbedder from embedder.py
        similarity_threshold: float = 0.9,
        max_size: int = 1000,
        default_ttl: Optional[float] = None
    ):
        """
        Args:
            embedder: Embedder instance for generating query embeddings
            similarity_threshold: Minimum similarity to consider a hit
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.embedder = embedder
        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        self._cache: Dict[str, CacheEntry] = {}
        self._embeddings: Dict[str, Any] = {}  # key -> embedding
        self._stats = CacheStats()
        self._lock = threading.RLock()
    
    def _compute_similarity(self, emb1, emb2) -> float:
        """Compute cosine similarity between embeddings."""
        import numpy as np
        dot = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value using semantic similarity."""
        with self._lock:
            # First try exact match
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    entry.touch()
                    self._stats.hits += 1
                    return entry.value
                else:
                    del self._cache[key]
                    del self._embeddings[key]
            
            # Try semantic match
            query_emb = self.embedder.embed_query(key)
            
            best_match = None
            best_similarity = 0.0
            
            for cached_key, cached_emb in self._embeddings.items():
                if cached_key not in self._cache:
                    continue
                
                entry = self._cache[cached_key]
                if entry.is_expired():
                    continue
                
                similarity = self._compute_similarity(query_emb, cached_emb)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = cached_key
            
            if best_match and best_similarity >= self.similarity_threshold:
                entry = self._cache[best_match]
                entry.touch()
                self._stats.hits += 1
                return entry.value
            
            self._stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.default_ttl
            )
            self._embeddings[key] = self.embedder.embed_query(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._embeddings[key]
                return True
            return False
    
    def clear(self):
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
            self._embeddings.clear()
            self._stats = CacheStats()
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                size=len(self._cache),
                evictions=self._stats.evictions
            )
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].accessed_at
        )
        
        del self._cache[lru_key]
        if lru_key in self._embeddings:
            del self._embeddings[lru_key]
        self._stats.evictions += 1


class CacheManager:
    """
    Manages multiple cache layers for RAG pipeline.
    
    Provides unified interface for caching embeddings,
    retrieval results, and generated responses.
    """
    
    def __init__(
        self,
        embedding_cache: Optional[BaseCache] = None,
        retrieval_cache: Optional[BaseCache] = None,
        response_cache: Optional[BaseCache] = None
    ):
        self.embedding_cache = embedding_cache or MemoryCache(max_size=10000)
        self.retrieval_cache = retrieval_cache or MemoryCache(max_size=1000)
        self.response_cache = response_cache or MemoryCache(max_size=500)
    
    def cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_embedding(self, text: str) -> Optional[Any]:
        """Get cached embedding."""
        key = self.cache_key("emb", text)
        return self.embedding_cache.get(key)
    
    def set_embedding(self, text: str, embedding: Any):
        """Cache embedding."""
        key = self.cache_key("emb", text)
        self.embedding_cache.set(key, embedding)
    
    def get_retrieval(self, query: str, top_k: int) -> Optional[List]:
        """Get cached retrieval results."""
        key = self.cache_key("ret", query, top_k)
        return self.retrieval_cache.get(key)
    
    def set_retrieval(self, query: str, top_k: int, results: List):
        """Cache retrieval results."""
        key = self.cache_key("ret", query, top_k)
        # Convert to serializable format
        self.retrieval_cache.set(key, results)
    
    def get_response(self, query: str, context_hash: str) -> Optional[str]:
        """Get cached response."""
        key = self.cache_key("resp", query, context_hash)
        return self.response_cache.get(key)
    
    def set_response(self, query: str, context_hash: str, response: str):
        """Cache response."""
        key = self.cache_key("resp", query, context_hash)
        self.response_cache.set(key, response)
    
    def clear_all(self):
        """Clear all caches."""
        self.embedding_cache.clear()
        self.retrieval_cache.clear()
        self.response_cache.clear()
    
    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all caches."""
        return {
            "embedding": self.embedding_cache.get_stats(),
            "retrieval": self.retrieval_cache.get_stats(),
            "response": self.response_cache.get_stats()
        }


def get_cache(
    backend: str = "memory",
    **kwargs
) -> BaseCache:
    """
    Factory function to get cache by backend name.
    
    Args:
        backend: One of 'memory', 'disk', 'redis'
        **kwargs: Backend-specific arguments
    
    Returns:
        BaseCache instance
    """
    backends = {
        "memory": MemoryCache,
        "disk": DiskCache,
        "redis": RedisCache,
    }
    
    if backend not in backends:
        raise ValueError(
            f"Unknown backend: {backend}. "
            f"Available: {list(backends.keys())}"
        )
    
    return backends[backend](**kwargs)
