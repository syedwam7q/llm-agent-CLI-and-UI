"""
LLM integration module supporting multiple providers.
"""
import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from abc import ABC, abstractmethod
from dataclasses import dataclass
import openai
from anthropic import Anthropic

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from config import settings


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # 'system', 'user', 'assistant', 'function'
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None


@dataclass
class FunctionCall:
    """Represents a function call from the LLM."""
    name: str
    arguments: Dict[str, Any]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """Generate a chat completion."""
        pass
    
    @abstractmethod
    async def stream_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def chat_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """Generate a chat completion using OpenAI."""
        openai_messages = []
        for msg in messages:
            openai_msg = {"role": msg.role, "content": msg.content}
            
            # Add name for function messages (required by OpenAI)
            if msg.role == "function" and msg.name:
                openai_msg["name"] = msg.name
            
            # Add function_call for assistant messages with function calls
            if msg.function_call:
                openai_msg["function_call"] = msg.function_call
            
            openai_messages.append(openai_msg)
        
        kwargs = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature or settings.agent_temperature,
            "max_tokens": max_tokens or settings.agent_max_tokens,
            "stream": stream
        }
        
        if functions:
            kwargs["functions"] = functions
            kwargs["function_call"] = "auto"
        
        response = await self.client.chat.completions.create(**kwargs)
        
        if stream:
            return response
        
        message = response.choices[0].message
        
        # Handle function calls
        if hasattr(message, 'function_call') and message.function_call:
            return FunctionCall(
                name=message.function_call.name,
                arguments=json.loads(message.function_call.arguments)
            )
        
        return message.content
    
    async def stream_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        stream = await self.chat_completion(
            messages, functions, temperature, max_tokens, stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    async def chat_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """Generate a chat completion using Anthropic."""
        # Convert messages to Anthropic format
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message += msg.content + "\n"
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        kwargs = {
            "model": self.model,
            "messages": claude_messages,
            "temperature": temperature or settings.agent_temperature,
            "max_tokens": max_tokens or settings.agent_max_tokens,
            "stream": stream
        }
        
        if system_message:
            kwargs["system"] = system_message.strip()
        
        # Note: Anthropic doesn't support function calling in the same way
        # We'll handle this through prompt engineering
        
        response = await asyncio.to_thread(
            self.client.messages.create, **kwargs
        )
        
        if stream:
            return response
        
        return response.content[0].text
    
    async def stream_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        # Anthropic streaming implementation would go here
        # For now, fall back to non-streaming
        content = await self.chat_completion(
            messages, functions, temperature, max_tokens, stream=False
        )
        yield content


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and fallback when no API keys are available."""
    
    def __init__(self):
        pass
    
    async def chat_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """Generate a mock chat completion."""
        if stream:
            return self._mock_stream()
        
        # Check if this looks like a function call request
        if functions and len(functions) > 0:
            # Return a mock function call for testing
            return FunctionCall(
                name=functions[0]["name"],
                arguments={"expression": "2+2"} if functions[0]["name"] == "calculator" else {}
            )
        
        return "I'm a mock AI assistant. Please configure your API keys to use real LLM providers."
    
    async def stream_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Stream a mock chat completion."""
        response = "I'm a mock AI assistant. Please configure your API keys to use real LLM providers."
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.1)
    
    def _mock_stream(self):
        """Return a mock stream object."""
        return self.stream_completion([])


class LLMManager:
    """Manages LLM providers and routing."""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers."""
        # OpenAI
        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.agent_model
            )
            if not self.default_provider:
                self.default_provider = "openai"
        
        # Anthropic
        if settings.anthropic_api_key:
            self.providers["anthropic"] = AnthropicProvider(
                api_key=settings.anthropic_api_key
            )
            if not self.default_provider:
                self.default_provider = "anthropic"
        
        # Mock provider as fallback
        if not self.default_provider:
            self.providers["mock"] = MockLLMProvider()
            self.default_provider = "mock"
    
    def get_provider(self, provider_name: Optional[str] = None) -> LLMProvider:
        """Get a specific provider or the default one."""
        provider_name = provider_name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return self.providers[provider_name]
    
    async def chat_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Generate a chat completion using the specified or default provider."""
        llm_provider = self.get_provider(provider)
        return await llm_provider.chat_completion(messages, functions, **kwargs)
    
    async def stream_completion(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        llm_provider = self.get_provider(provider)
        async for chunk in llm_provider.stream_completion(messages, functions, **kwargs):
            yield chunk


# Global LLM manager instance
llm_manager = LLMManager()


def get_llm_manager() -> LLMManager:
    """Get the global LLM manager instance."""
    return llm_manager