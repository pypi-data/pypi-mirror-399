"""
Chunker - Document chunking strategies.
"""

import re
import logging
from typing import List, Optional
from dataclasses import dataclass

from .types import Document, Chunk, ChunkingStrategy

logger = logging.getLogger(__name__)


class Chunker:
    """
    Document Chunker.
    
    Splits documents into optimally-sized chunks for embedding
    and retrieval.
    
    Examples:
        >>> chunker = Chunker(chunk_size=512, chunk_overlap=50)
        >>> chunks = chunker.chunk(document)
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "recursive",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
    
    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk a document.
        
        Args:
            document: Document to chunk
        
        Returns:
            List of Chunk objects
        """
        if self.strategy == "recursive":
            return self._recursive_chunk(document)
        elif self.strategy == "sentence":
            return self._sentence_chunk(document)
        elif self.strategy == "paragraph":
            return self._paragraph_chunk(document)
        else:
            return self._fixed_chunk(document)
    
    def _fixed_chunk(self, document: Document) -> List[Chunk]:
        """Fixed-size chunking."""
        chunks = []
        text = document.content
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append(Chunk(
                content=chunk_text,
                doc_id=document.doc_id,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                metadata=document.metadata.copy(),
            ))
            
            start = end - self.chunk_overlap
            chunk_index += 1
        
        return chunks
    
    def _recursive_chunk(self, document: Document) -> List[Chunk]:
        """Recursive chunking with semantic boundaries."""
        separators = ["\n\n", "\n", ". ", " "]
        return self._split_recursive(
            document.content,
            document.doc_id,
            document.metadata,
            separators,
        )
    
    def _split_recursive(
        self,
        text: str,
        doc_id: str,
        metadata: dict,
        separators: List[str],
        chunk_index: int = 0,
    ) -> List[Chunk]:
        """Recursively split text."""
        chunks = []
        
        if len(text) <= self.chunk_size:
            return [Chunk(
                content=text,
                doc_id=doc_id,
                chunk_index=chunk_index,
                metadata=metadata.copy(),
            )]
        
        separator = separators[0] if separators else ""
        parts = text.split(separator)
        
        current_chunk = ""
        for part in parts:
            if len(current_chunk) + len(part) + len(separator) <= self.chunk_size:
                current_chunk += part + separator
            else:
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        doc_id=doc_id,
                        chunk_index=len(chunks),
                        metadata=metadata.copy(),
                    ))
                
                if len(part) > self.chunk_size and len(separators) > 1:
                    sub_chunks = self._split_recursive(
                        part, doc_id, metadata, separators[1:], len(chunks)
                    )
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = part + separator
        
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                doc_id=doc_id,
                chunk_index=len(chunks),
                metadata=metadata.copy(),
            ))
        
        return chunks
    
    def _sentence_chunk(self, document: Document) -> List[Chunk]:
        """Sentence-based chunking."""
        sentences = re.split(r'(?<=[.!?])\s+', document.content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        doc_id=document.doc_id,
                        chunk_index=len(chunks),
                        metadata=document.metadata.copy(),
                    ))
                current_chunk = sentence + " "
        
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                doc_id=document.doc_id,
                chunk_index=len(chunks),
                metadata=document.metadata.copy(),
            ))
        
        return chunks
    
    def _paragraph_chunk(self, document: Document) -> List[Chunk]:
        """Paragraph-based chunking."""
        paragraphs = document.content.split("\n\n")
        chunks = []
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                chunks.append(Chunk(
                    content=para.strip(),
                    doc_id=document.doc_id,
                    chunk_index=i,
                    metadata=document.metadata.copy(),
                ))
        
        return chunks
