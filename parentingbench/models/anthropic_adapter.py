"""Anthropic API adapter."""

import os
from typing import Optional, Dict

from .base import BaseModel


class AnthropicModel(BaseModel):
    """Adapter for Anthropic Claude models."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Anthropic model.

        Args:
            model_name: Anthropic model name (default: claude-3-5-sonnet-20241022)
            api_key: Anthropic API key (default: reads from ANTHROPIC_API_KEY env var)
            **kwargs: Additional arguments
        """
        super().__init__(model_name, api_key, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        Generate response using Anthropic API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional Anthropic parameters

        Returns:
            Generated response
        """
        message_kwargs = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }

        if system_prompt:
            message_kwargs["system"] = system_prompt

        response = self.client.messages.create(**message_kwargs)

        return response.content[0].text

    def get_model_info(self) -> Dict:
        """Get Anthropic model information."""
        return {"provider": "anthropic", "model_name": self.model_name, "api_version": "2023-06-01"}
