"""
Response generation module for Production RAG.

Handles LLM integration for generating responses from retrieved context.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, Union
from datetime import datetime

from .types import Chunk, Query, Response, RetrievalResult


@dataclass
class GeneratorConfig:
    """Configuration for response generator."""
    
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    
    # RAG-specific settings
    include_sources: bool = True
    citation_style: str = "inline"  # inline, footnote, none
    max_context_chunks: int = 5
    context_template: str = "Context:\n{context}\n\nQuestion: {query}"
    system_prompt: Optional[str] = None


@dataclass
class GenerationResult:
    """Result from response generation."""
    
    response: str
    sources: List[RetrievalResult] = field(default_factory=list)
    model: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseGenerator(ABC):
    """Abstract base class for generators."""
    
    @abstractmethod
    def generate(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> GenerationResult:
        """Generate response from query and context."""
        pass
    
    def generate_stream(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> Iterator[str]:
        """Stream response generation."""
        result = self.generate(query, context, **kwargs)
        yield result.response


class OpenAIGenerator(BaseGenerator):
    """Generator using OpenAI API."""
    
    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
    
Guidelines:
- Answer based ONLY on the provided context
- If the context doesn't contain the answer, say so clearly
- Be concise and accurate
- Cite sources when possible using [1], [2], etc."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[GeneratorConfig] = None
    ):
        self.api_key = api_key
        self.config = config or GeneratorConfig()
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
    
    def _format_context(self, results: List[RetrievalResult]) -> str:
        """Format retrieval results as context string."""
        context_parts = []
        
        for i, result in enumerate(results[:self.config.max_context_chunks], 1):
            source_info = ""
            if result.chunk.metadata.get("source"):
                source_info = f" (Source: {result.chunk.metadata['source']})"
            
            context_parts.append(
                f"[{i}]{source_info}:\n{result.chunk.content}"
            )
        
        return "\n\n".join(context_parts)
    
    def generate(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> GenerationResult:
        """Generate response using OpenAI."""
        import time
        start_time = time.time()
        
        client = self._get_client()
        
        # Format context
        context_str = self._format_context(context)
        
        # Build messages
        system_prompt = self.config.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        user_message = self.config.context_template.format(
            context=context_str,
            query=query
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Generate response
        response = client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            stop=self.config.stop_sequences
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return GenerationResult(
            response=response.choices[0].message.content,
            sources=context[:self.config.max_context_chunks],
            model=response.model,
            tokens_used=response.usage.total_tokens if response.usage else 0,
            latency_ms=latency_ms,
            metadata={
                "finish_reason": response.choices[0].finish_reason
            }
        )
    
    def generate_stream(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> Iterator[str]:
        """Stream response generation."""
        client = self._get_client()
        
        context_str = self._format_context(context)
        system_prompt = self.config.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        user_message = self.config.context_template.format(
            context=context_str,
            query=query
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        stream = client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicGenerator(BaseGenerator):
    """Generator using Anthropic Claude API."""
    
    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
    
Answer based ONLY on the provided context. If the context doesn't contain the answer, say so clearly.
Be concise and accurate. Cite sources when possible using [1], [2], etc."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[GeneratorConfig] = None
    ):
        self.api_key = api_key
        self.config = config or GeneratorConfig(model="claude-sonnet-4-20250514")
        self._client = None
    
    def _get_client(self):
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic required. Install with: pip install anthropic"
                )
        return self._client
    
    def _format_context(self, results: List[RetrievalResult]) -> str:
        """Format retrieval results as context string."""
        context_parts = []
        
        for i, result in enumerate(results[:self.config.max_context_chunks], 1):
            source_info = ""
            if result.chunk.metadata.get("source"):
                source_info = f" (Source: {result.chunk.metadata['source']})"
            
            context_parts.append(
                f"[{i}]{source_info}:\n{result.chunk.content}"
            )
        
        return "\n\n".join(context_parts)
    
    def generate(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> GenerationResult:
        """Generate response using Anthropic."""
        import time
        start_time = time.time()
        
        client = self._get_client()
        
        context_str = self._format_context(context)
        system_prompt = self.config.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        user_message = self.config.context_template.format(
            context=context_str,
            query=query
        )
        
        response = client.messages.create(
            model=kwargs.get("model", self.config.model),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return GenerationResult(
            response=response.content[0].text,
            sources=context[:self.config.max_context_chunks],
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            latency_ms=latency_ms,
            metadata={
                "stop_reason": response.stop_reason
            }
        )
    
    def generate_stream(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> Iterator[str]:
        """Stream response generation."""
        client = self._get_client()
        
        context_str = self._format_context(context)
        system_prompt = self.config.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        user_message = self.config.context_template.format(
            context=context_str,
            query=query
        )
        
        with client.messages.stream(
            model=kwargs.get("model", self.config.model),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        ) as stream:
            for text in stream.text_stream:
                yield text


class CustomGenerator(BaseGenerator):
    """
    Generator using custom LLM function.
    
    Allows integration with any LLM backend.
    
    Example:
        def my_llm(prompt: str) -> str:
            # Your LLM logic here
            return response
        
        generator = CustomGenerator(my_llm)
    """
    
    def __init__(
        self,
        llm_fn: Callable[[str], str],
        config: Optional[GeneratorConfig] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Args:
            llm_fn: Function that takes prompt string and returns response
            config: Generator configuration
            system_prompt: System prompt to prepend
        """
        self.llm_fn = llm_fn
        self.config = config or GeneratorConfig()
        self.system_prompt = system_prompt
    
    def _format_context(self, results: List[RetrievalResult]) -> str:
        """Format retrieval results as context string."""
        context_parts = []
        
        for i, result in enumerate(results[:self.config.max_context_chunks], 1):
            context_parts.append(f"[{i}]: {result.chunk.content}")
        
        return "\n\n".join(context_parts)
    
    def generate(
        self,
        query: str,
        context: List[RetrievalResult],
        **kwargs
    ) -> GenerationResult:
        """Generate response using custom LLM."""
        import time
        start_time = time.time()
        
        context_str = self._format_context(context)
        
        prompt_parts = []
        if self.system_prompt:
            prompt_parts.append(self.system_prompt)
        
        prompt_parts.append(
            self.config.context_template.format(
                context=context_str,
                query=query
            )
        )
        
        full_prompt = "\n\n".join(prompt_parts)
        response = self.llm_fn(full_prompt)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return GenerationResult(
            response=response,
            sources=context[:self.config.max_context_chunks],
            model="custom",
            latency_ms=latency_ms
        )


class PromptBuilder:
    """
    Helper class for building RAG prompts.
    
    Supports multiple prompt strategies and templates.
    """
    
    TEMPLATES = {
        "default": """Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query}
Answer:""",
        
        "chat": """You are a helpful assistant. Use the following context to answer the user's question.

Context:
{context}

User: {query}
Assistant:""",
        
        "academic": """Based on the following sources, provide a well-cited response to the question.

Sources:
{context}

Question: {query}

Please cite sources using [1], [2], etc. format.""",
        
        "concise": """Context: {context}

Q: {query}
A:"""
    }
    
    def __init__(self, template_name: str = "default"):
        if template_name in self.TEMPLATES:
            self.template = self.TEMPLATES[template_name]
        else:
            self.template = template_name
    
    def build(
        self,
        query: str,
        context: List[RetrievalResult],
        max_chunks: int = 5
    ) -> str:
        """Build prompt from query and context."""
        context_parts = []
        
        for i, result in enumerate(context[:max_chunks], 1):
            content = result.chunk.content
            source = result.chunk.metadata.get("source", f"Source {i}")
            context_parts.append(f"[{i}] {source}:\n{content}")
        
        context_str = "\n\n".join(context_parts)
        
        return self.template.format(
            context=context_str,
            query=query
        )
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names."""
        return list(cls.TEMPLATES.keys())


def get_generator(
    provider: str = "openai",
    **kwargs
) -> BaseGenerator:
    """
    Factory function to get generator by provider name.
    
    Args:
        provider: One of 'openai', 'anthropic', 'custom'
        **kwargs: Provider-specific arguments
    
    Returns:
        BaseGenerator instance
    
    Example:
        generator = get_generator("openai", api_key="sk-...")
    """
    providers = {
        "openai": OpenAIGenerator,
        "anthropic": AnthropicGenerator,
    }
    
    if provider not in providers:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available: {list(providers.keys())}"
        )
    
    return providers[provider](**kwargs)
