# Production RAG

[![PyPI version](https://badge.fury.io/py/production-rag.svg)](https://badge.fury.io/py/production-rag)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise-ready Retrieval-Augmented Generation framework** that's actually production-ready. Better than LangChain and LlamaIndex for real-world deployments.

## Why Production RAG?

Existing RAG frameworks (LangChain, LlamaIndex) are great for prototyping but fall short in production:

| Feature | Production RAG | LangChain | LlamaIndex |
|---------|---------------|-----------|------------|
| Zero dependencies core | ✅ | ❌ | ❌ |
| Type-safe throughout | ✅ | ❌ | Partial |
| Built-in caching | ✅ | Manual | Manual |
| Async-first | ✅ | Partial | Partial |
| Observability | ✅ Built-in | Manual | Manual |
| Memory efficient | ✅ | ❌ | ❌ |
| Easy to debug | ✅ | ❌ | ❌ |

## Installation

```bash
# Core (zero dependencies except numpy)
pip install production-rag

# With embeddings support
pip install production-rag[embeddings]

# With OpenAI
pip install production-rag[openai]

# With Anthropic Claude
pip install production-rag[anthropic]

# Full installation
pip install production-rag[all]
```

## Quick Start

### 30-Second Example

```python
from production_rag import RAGPipeline

# Create pipeline
rag = RAGPipeline()

# Add documents
rag.add_documents([
    "Python is a programming language created by Guido van Rossum.",
    "Machine learning is a subset of artificial intelligence.",
    "RAG combines retrieval with generation for better LLM responses.",
])

# Query
response = rag.query("What is Python?")
print(response.answer)
print(f"Sources: {response.sources}")
print(f"Confidence: {response.confidence}")
```

### Production Example

```python
from production_rag import (
    RAGPipeline,
    PipelineConfig,
    Document,
    ChunkingStrategy,
)

# Configure for production
config = PipelineConfig(
    chunking_strategy=ChunkingStrategy.RECURSIVE,
    chunk_size=512,
    chunk_overlap=50,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    rerank_enabled=True,
    cache_enabled=True,
    cache_ttl=3600,
)

# Create pipeline
rag = RAGPipeline(config)

# Add documents with metadata
documents = [
    Document(
        content="Your document content here...",
        metadata={"source": "manual.pdf", "page": 1, "category": "technical"}
    ),
    Document(
        content="Another document...",
        metadata={"source": "faq.md", "category": "support"}
    ),
]

rag.add_documents(documents)

# Query with filters
response = rag.query(
    "How do I configure the system?",
    top_k=5,
    filter={"category": "technical"},
    include_sources=True,
)

print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence:.2f}")
for source in response.sources:
    print(f"  - {source.metadata['source']}: {source.relevance_score:.2f}")
```

## Core Components

### 1. Document Processing

```python
from production_rag import Document, DocumentType

# Text documents
doc = Document(content="Your text here", doc_type=DocumentType.TEXT)

# From files (with optional dependencies)
doc = Document.from_file("document.pdf")  # Requires [pdf]
doc = Document.from_file("document.docx")  # Requires [docx]
doc = Document.from_file("page.html")      # Requires [html]
doc = Document.from_file("data.json")
doc = Document.from_file("data.csv")
doc = Document.from_file("readme.md")
```

### 2. Chunking Strategies

```python
from production_rag import Chunker, ChunkingStrategy

chunker = Chunker(
    strategy=ChunkingStrategy.RECURSIVE,  # or FIXED, SENTENCE, PARAGRAPH
    chunk_size=512,
    chunk_overlap=50,
)

chunks = chunker.chunk(document)
```

**Available Strategies:**
- `FIXED` - Fixed character windows
- `RECURSIVE` - Smart recursive splitting (recommended)
- `SENTENCE` - Sentence-based splitting
- `PARAGRAPH` - Paragraph-based splitting

### 3. Embeddings

```python
from production_rag import Embedder

# Default (sentence-transformers)
embedder = Embedder()

# OpenAI
embedder = Embedder(provider="openai", model="text-embedding-3-small")

# Custom
embedder = Embedder(provider="custom", embed_fn=your_function)

# Generate embeddings
embeddings = embedder.embed(["text 1", "text 2"])
```

### 4. Vector Store

```python
from production_rag import VectorStore

# In-memory (default)
store = VectorStore()

# With persistence
store = VectorStore(persist_path="./vector_db")

# Add vectors
store.add(embeddings, chunks, metadata)

# Search
results = store.search(query_embedding, top_k=10)

# Save/Load
store.save("./my_store")
store = VectorStore.load("./my_store")
```

### 5. Retriever

```python
from production_rag import Retriever, RetrieverConfig

config = RetrieverConfig(
    top_k=10,
    similarity_threshold=0.7,
    hybrid_search=True,  # Combines dense + sparse
    hybrid_alpha=0.7,    # Weight for dense search
)

retriever = Retriever(vector_store, embedder, config)
results = retriever.retrieve("your query")
```

### 6. Reranker

```python
from production_rag import Reranker

# Cross-encoder reranking (most accurate)
reranker = Reranker(model="cross-encoder/ms-marco-MiniLM-L-6-v2")

# Rerank results
reranked = reranker.rerank(query, results, top_k=5)
```

### 7. Generator

```python
from production_rag import Generator, GeneratorConfig

# OpenAI
generator = Generator(
    provider="openai",
    model="gpt-4",
    config=GeneratorConfig(
        temperature=0.7,
        max_tokens=1024,
        system_prompt="You are a helpful assistant.",
    )
)

# Anthropic Claude
generator = Generator(
    provider="anthropic",
    model="claude-3-sonnet-20240229",
)

# Generate response
response = generator.generate(query, context_chunks)
```

### 8. Caching

```python
from production_rag import RAGPipeline, PipelineConfig

config = PipelineConfig(
    cache_enabled=True,
    cache_ttl=3600,  # 1 hour
    cache_backend="memory",  # or "redis", "disk"
)

rag = RAGPipeline(config)
# Subsequent identical queries return cached results
```

## Advanced Usage

### Async Support

```python
import asyncio
from production_rag import AsyncRAGPipeline

async def main():
    rag = AsyncRAGPipeline()
    await rag.add_documents(documents)
    
    # Concurrent queries
    queries = ["Query 1", "Query 2", "Query 3"]
    responses = await asyncio.gather(*[
        rag.query(q) for q in queries
    ])
    
asyncio.run(main())
```

### Batch Processing

```python
# Add documents in batches
rag.add_documents(large_document_list, batch_size=100)

# Batch queries
responses = rag.query_batch(
    ["Query 1", "Query 2", "Query 3"],
    batch_size=10,
)
```

### Custom Components

```python
from production_rag import RAGPipeline, Embedder, VectorStore, Generator

# Use your own components
rag = RAGPipeline(
    embedder=MyCustomEmbedder(),
    vector_store=MyCustomVectorStore(),
    generator=MyCustomGenerator(),
)
```

### Observability & Metrics

```python
from production_rag import RAGPipeline

rag = RAGPipeline()
rag.add_documents(documents)
response = rag.query("test query")

# Access metrics
metrics = rag.get_metrics()
print(f"Total queries: {metrics.total_queries}")
print(f"Average latency: {metrics.avg_latency_ms:.2f}ms")
print(f"Cache hit rate: {metrics.cache_hit_rate:.2%}")
print(f"Documents indexed: {metrics.documents_indexed}")

# Per-query metrics
print(f"Retrieval time: {response.metrics.retrieval_ms:.2f}ms")
print(f"Generation time: {response.metrics.generation_ms:.2f}ms")
print(f"Total time: {response.metrics.total_ms:.2f}ms")
```

### Filtering & Metadata

```python
# Add documents with rich metadata
docs = [
    Document(
        content="...",
        metadata={
            "source": "manual.pdf",
            "category": "technical",
            "date": "2024-01-15",
            "department": "engineering",
        }
    )
]
rag.add_documents(docs)

# Filter queries
response = rag.query(
    "How to deploy?",
    filter={
        "category": "technical",
        "department": "engineering",
    }
)
```

### Streaming Responses

```python
# Stream generation
for chunk in rag.query_stream("What is RAG?"):
    print(chunk, end="", flush=True)
```

## Pipeline Persistence

```python
# Save entire pipeline
rag.save("./my_rag_pipeline")

# Load pipeline
rag = RAGPipeline.load("./my_rag_pipeline")
```

## Integrations

### FastAPI

```python
from fastapi import FastAPI
from production_rag import RAGPipeline

app = FastAPI()
rag = RAGPipeline.load("./my_pipeline")

@app.post("/query")
async def query(q: str):
    response = await rag.aquery(q)
    return {
        "answer": response.answer,
        "sources": [s.metadata for s in response.sources],
        "confidence": response.confidence,
    }
```

### LangChain Compatibility

```python
from production_rag.integrations import LangChainRetriever

# Use as LangChain retriever
retriever = LangChainRetriever(rag_pipeline)
chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
```

## Configuration Reference

```python
from production_rag import PipelineConfig, ChunkingStrategy

config = PipelineConfig(
    # Chunking
    chunking_strategy=ChunkingStrategy.RECURSIVE,
    chunk_size=512,
    chunk_overlap=50,
    
    # Embeddings
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    embedding_batch_size=32,
    
    # Retrieval
    top_k=10,
    similarity_threshold=0.5,
    hybrid_search=False,
    
    # Reranking
    rerank_enabled=True,
    rerank_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    rerank_top_k=5,
    
    # Generation
    generator_provider="openai",
    generator_model="gpt-4",
    temperature=0.7,
    max_tokens=1024,
    
    # Caching
    cache_enabled=True,
    cache_ttl=3600,
    cache_backend="memory",
    
    # Performance
    batch_size=100,
    num_workers=4,
)
```

## Performance Tips

1. **Use appropriate chunk sizes** - 256-512 tokens works well for most cases
2. **Enable caching** - Dramatically improves repeated query performance
3. **Use reranking** - Improves relevance at minimal latency cost
4. **Batch operations** - Use batch methods for bulk processing
5. **Async for concurrency** - Use async methods for concurrent requests

## API Reference

### RAGPipeline

| Method | Description |
|--------|-------------|
| `add_documents(docs)` | Add documents to the pipeline |
| `query(q, **kwargs)` | Query the pipeline |
| `query_batch(queries)` | Batch query |
| `query_stream(q)` | Stream response |
| `search(q, top_k)` | Search without generation |
| `save(path)` | Save pipeline |
| `load(path)` | Load pipeline |
| `get_metrics()` | Get pipeline metrics |

### Document

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | str | Document text |
| `metadata` | dict | Document metadata |
| `doc_type` | DocumentType | Type of document |
| `doc_id` | str | Unique identifier |

### Response

| Attribute | Type | Description |
|-----------|------|-------------|
| `answer` | str | Generated answer |
| `sources` | List[Chunk] | Source chunks |
| `confidence` | float | Confidence score |
| `metrics` | ResponseMetrics | Timing metrics |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Pranay M**

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
