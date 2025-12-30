"""LiteLLM adapter for unified access to 100+ LLM providers."""

import os
from typing import Optional, Dict

from .base import BaseModel


class LiteLLMModel(BaseModel):
    """
    Adapter for LiteLLM - unified interface to 100+ LLM providers.

    Supports: OpenAI, Anthropic, Google (Gemini, VertexAI), Cohere, HuggingFace,
    Ollama, Together, Replicate, Bedrock, Azure, and many more.

    Examples:
        - OpenAI: "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"
        - Anthropic: "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"
        - Google: "gemini/gemini-2.0-flash-exp", "vertex_ai/gemini-pro"
        - Ollama (local): "ollama/llama3.2", "ollama/mistral"
        - HuggingFace: "huggingface/meta-llama/Llama-3.1-70B-Instruct"
        - Together: "together_ai/meta-llama/Llama-3-70b-chat-hf"
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize LiteLLM model.

        Args:
            model_name: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet-20241022", "ollama/llama3.2")
            api_key: Optional API key (LiteLLM will auto-detect from env vars)
            api_base: Optional API base URL for custom endpoints
            **kwargs: Additional LiteLLM arguments
        """
        super().__init__(model_name, api_key, **kwargs)
        self.api_base = api_base

        try:
            import litellm

            self.litellm = litellm

            # Configure LiteLLM
            if api_key:
                # Set API key based on provider
                provider = self._detect_provider(model_name)
                if provider == "openai":
                    os.environ["OPENAI_API_KEY"] = api_key
                elif provider == "anthropic":
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                elif provider == "gemini":
                    os.environ["GEMINI_API_KEY"] = api_key

            if api_base:
                litellm.api_base = api_base

        except ImportError:
            raise ImportError("litellm package not installed. Install with: pip install litellm")

    def _detect_provider(self, model_name: str) -> str:
        """Detect provider from model name."""
        if model_name.startswith("gpt") or model_name.startswith("o1"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        elif "gemini" in model_name.lower():
            return "gemini"
        elif "ollama" in model_name.lower():
            return "ollama"
        else:
            return "unknown"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        Generate response using LiteLLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional LiteLLM parameters

        Returns:
            Generated response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.litellm.completion(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"LiteLLM generation failed: {e}")

    def get_model_info(self) -> Dict:
        """Get LiteLLM model information."""
        provider = self._detect_provider(self.model_name)
        return {
            "provider": f"litellm:{provider}",
            "model_name": self.model_name,
            "api_base": self.api_base,
            "supports_streaming": True,
            "supports_function_calling": True,
        }
