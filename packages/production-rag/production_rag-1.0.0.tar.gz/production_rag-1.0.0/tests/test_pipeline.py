"""Tests for production-rag package."""

import pytest
import numpy as np
from production_rag import (
    RAGPipeline,
    PipelineConfig,
    Document,
    DocumentType,
    Chunk,
    ChunkingStrategy,
    Chunker,
    VectorStore,
    Retriever,
    RetrieverConfig,
)


class TestDocument:
    """Tests for Document class."""

    def test_document_creation(self):
        """Test basic document creation."""
        doc = Document(content="Test content")
        assert doc.content == "Test content"
        assert doc.doc_id is not None
        assert doc.metadata == {}

    def test_document_with_metadata(self):
        """Test document with metadata."""
        doc = Document(
            content="Test content",
            metadata={"source": "test.txt", "page": 1},
        )
        assert doc.metadata["source"] == "test.txt"
        assert doc.metadata["page"] == 1

    def test_document_with_type(self):
        """Test document with type."""
        doc = Document(
            content="Test content",
            doc_type=DocumentType.TEXT,
        )
        assert doc.doc_type == DocumentType.TEXT


class TestChunker:
    """Tests for Chunker class."""

    def test_fixed_chunking(self):
        """Test fixed chunking strategy."""
        chunker = Chunker(
            strategy=ChunkingStrategy.FIXED,
            chunk_size=100,
            chunk_overlap=20,
        )
        doc = Document(content="A" * 250)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_sentence_chunking(self):
        """Test sentence chunking strategy."""
        chunker = Chunker(
            strategy=ChunkingStrategy.SENTENCE,
            chunk_size=100,
        )
        doc = Document(content="First sentence. Second sentence. Third sentence.")
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1

    def test_recursive_chunking(self):
        """Test recursive chunking strategy."""
        chunker = Chunker(
            strategy=ChunkingStrategy.RECURSIVE,
            chunk_size=50,
            chunk_overlap=10,
        )
        doc = Document(content="Paragraph one.\n\nParagraph two.\n\nParagraph three.")
        chunks = chunker.chunk(doc)
        assert len(chunks) >= 1


class TestVectorStore:
    """Tests for VectorStore class."""

    def test_vector_store_creation(self):
        """Test vector store creation."""
        store = VectorStore()
        assert store is not None

    def test_add_and_search(self):
        """Test adding and searching vectors."""
        store = VectorStore()
        
        # Create sample embeddings
        embeddings = np.random.rand(5, 128).astype(np.float32)
        chunks = [
            Chunk(content=f"Chunk {i}", chunk_id=str(i), doc_id="doc1")
            for i in range(5)
        ]
        
        store.add(embeddings, chunks)
        
        # Search
        query_embedding = np.random.rand(128).astype(np.float32)
        results = store.search(query_embedding, top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(r, tuple) for r in results)

    def test_delete_by_doc_id(self):
        """Test deleting vectors by document ID."""
        store = VectorStore()
        
        embeddings = np.random.rand(3, 128).astype(np.float32)
        chunks = [
            Chunk(content=f"Chunk {i}", chunk_id=str(i), doc_id="doc1")
            for i in range(3)
        ]
        store.add(embeddings, chunks)
        
        # Delete
        deleted = store.delete(doc_id="doc1")
        assert deleted == 3


class TestRetriever:
    """Tests for Retriever class."""

    def test_retriever_creation(self):
        """Test retriever creation."""
        store = VectorStore()
        config = RetrieverConfig(top_k=5)
        retriever = Retriever(vector_store=store, config=config)
        assert retriever is not None


class TestRAGPipeline:
    """Tests for RAGPipeline class."""

    def test_pipeline_creation(self):
        """Test pipeline creation with default config."""
        pipeline = RAGPipeline()
        assert pipeline is not None

    def test_pipeline_with_config(self):
        """Test pipeline creation with custom config."""
        config = PipelineConfig(
            chunk_size=256,
            chunk_overlap=25,
            chunking_strategy=ChunkingStrategy.RECURSIVE,
        )
        pipeline = RAGPipeline(config)
        assert pipeline is not None

    def test_add_documents_strings(self):
        """Test adding documents as strings."""
        pipeline = RAGPipeline()
        pipeline.add_documents([
            "First document content.",
            "Second document content.",
        ])
        assert pipeline.document_count == 2

    def test_add_documents_objects(self):
        """Test adding Document objects."""
        pipeline = RAGPipeline()
        docs = [
            Document(content="First doc", metadata={"source": "a.txt"}),
            Document(content="Second doc", metadata={"source": "b.txt"}),
        ]
        pipeline.add_documents(docs)
        assert pipeline.document_count == 2

    def test_search(self):
        """Test search functionality."""
        pipeline = RAGPipeline()
        pipeline.add_documents([
            "Python is a programming language.",
            "JavaScript is used for web development.",
            "Machine learning is a subset of AI.",
        ])
        
        results = pipeline.search("programming language", top_k=2)
        assert len(results) <= 2

    def test_pipeline_metrics(self):
        """Test metrics tracking."""
        pipeline = RAGPipeline()
        pipeline.add_documents(["Test document."])
        
        metrics = pipeline.get_metrics()
        assert metrics.documents_indexed == 1


class TestPipelineConfig:
    """Tests for PipelineConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.chunking_strategy == ChunkingStrategy.RECURSIVE

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PipelineConfig(
            chunk_size=256,
            chunk_overlap=25,
            chunking_strategy=ChunkingStrategy.SENTENCE,
            cache_enabled=True,
            cache_ttl=7200,
        )
        assert config.chunk_size == 256
        assert config.chunk_overlap == 25
        assert config.cache_enabled == True
        assert config.cache_ttl == 7200


class TestChunk:
    """Tests for Chunk class."""

    def test_chunk_creation(self):
        """Test chunk creation."""
        chunk = Chunk(
            content="Test chunk content",
            chunk_id="chunk_1",
            doc_id="doc_1",
        )
        assert chunk.content == "Test chunk content"
        assert chunk.chunk_id == "chunk_1"
        assert chunk.doc_id == "doc_1"

    def test_chunk_with_metadata(self):
        """Test chunk with metadata."""
        chunk = Chunk(
            content="Test chunk",
            chunk_id="chunk_1",
            doc_id="doc_1",
            metadata={"page": 1, "section": "intro"},
        )
        assert chunk.metadata["page"] == 1
        assert chunk.metadata["section"] == "intro"


# Integration tests
class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_end_to_end_pipeline(self):
        """Test complete pipeline from documents to search."""
        # Create pipeline
        config = PipelineConfig(
            chunk_size=100,
            chunk_overlap=10,
        )
        pipeline = RAGPipeline(config)
        
        # Add documents
        documents = [
            Document(
                content="Python is a versatile programming language known for its readability.",
                metadata={"category": "programming"}
            ),
            Document(
                content="Machine learning algorithms learn patterns from data.",
                metadata={"category": "ml"}
            ),
            Document(
                content="Natural language processing enables computers to understand text.",
                metadata={"category": "nlp"}
            ),
        ]
        pipeline.add_documents(documents)
        
        # Search
        results = pipeline.search("programming language", top_k=2)
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
