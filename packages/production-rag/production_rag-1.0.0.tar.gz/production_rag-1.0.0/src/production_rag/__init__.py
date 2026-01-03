"""
Production RAG - Enterprise-ready Retrieval Augmented Generation Framework
==========================================================================

A production-ready RAG framework that goes beyond LangChain/LlamaIndex
with better performance, reliability, and observability.

Author: Pranay M
License: MIT

Quick Start:
    >>> from production_rag import RAGPipeline
    >>> 
    >>> # Create pipeline
    >>> pipeline = RAGPipeline()
    >>> pipeline.add_documents(["doc1.pdf", "doc2.txt"])
    >>> 
    >>> # Query
    >>> response = pipeline.query("What is the main topic?")
    >>> print(response.answer)

Features:
    - Multi-format document support (PDF, DOCX, HTML, Markdown, JSON, CSV)
    - Multiple chunking strategies with overlap
    - Pluggable embedding backends (OpenAI, Sentence Transformers, Cohere)
    - Vector store with persistence
    - Advanced reranking (Cross-encoder, Cohere, RRF, LLM-based)
    - Multi-layer caching (Memory, Disk, Redis, Semantic)
    - LLM response generation (OpenAI, Anthropic, Custom)
    - Comprehensive metrics and observability
"""

__version__ = "1.0.0"
__author__ = "Pranay M"
__email__ = "pranay@example.com"

# Types
from .types import (
    Document,
    DocumentType,
    Chunk,
    ChunkingStrategy,
    Query,
    Response,
    RetrievalResult,
    PipelineMetrics,
)

# Core Pipeline
from .pipeline import RAGPipeline, PipelineConfig

# Vector Store
from .vectorstore import VectorStore

# Retriever
from .retriever import Retriever, RetrieverConfig

# Chunker
from .chunker import Chunker, ChunkerConfig

# Embedders
from .embedder import (
    BaseEmbedder,
    EmbedderConfig,
    SentenceTransformerEmbedder,
    OpenAIEmbedder,
    CohereEmbedder,
    SimpleEmbedder,
    HybridEmbedder,
    get_embedder,
)

# Rerankers
from .reranker import (
    BaseReranker,
    RerankerConfig,
    CrossEncoderReranker,
    CohereReranker,
    LLMReranker,
    RRFReranker,
    EnsembleReranker,
    get_reranker,
)

# Generators
from .generator import (
    BaseGenerator,
    GeneratorConfig,
    GenerationResult,
    OpenAIGenerator,
    AnthropicGenerator,
    CustomGenerator,
    PromptBuilder,
    get_generator,
)

# Caching
from .cache import (
    BaseCache,
    CacheEntry,
    CacheStats,
    MemoryCache,
    DiskCache,
    RedisCache,
    SemanticCache,
    CacheManager,
    get_cache,
)

__all__ = [
    # Types
    "Document",
    "DocumentType",
    "Chunk",
    "ChunkingStrategy",
    "Query",
    "Response",
    "RetrievalResult",
    "PipelineMetrics",
    # Core Pipeline
    "RAGPipeline",
    "PipelineConfig",
    # Vector Store
    "VectorStore",
    # Retriever
    "Retriever",
    "RetrieverConfig",
    # Chunker
    "Chunker",
    "ChunkerConfig",
    # Embedders
    "BaseEmbedder",
    "EmbedderConfig",
    "SentenceTransformerEmbedder",
    "OpenAIEmbedder",
    "CohereEmbedder",
    "SimpleEmbedder",
    "HybridEmbedder",
    "get_embedder",
    # Rerankers
    "BaseReranker",
    "RerankerConfig",
    "CrossEncoderReranker",
    "CohereReranker",
    "LLMReranker",
    "RRFReranker",
    "EnsembleReranker",
    "get_reranker",
    # Generators
    "BaseGenerator",
    "GeneratorConfig",
    "GenerationResult",
    "OpenAIGenerator",
    "AnthropicGenerator",
    "CustomGenerator",
    "PromptBuilder",
    "get_generator",
    # Caching
    "BaseCache",
    "CacheEntry",
    "CacheStats",
    "MemoryCache",
    "DiskCache",
    "RedisCache",
    "SemanticCache",
    "CacheManager",
    "get_cache",
]
