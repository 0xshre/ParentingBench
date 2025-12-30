"""OpenAI API adapter."""

import os

from .base import BaseModel


class OpenAIModel(BaseModel):
    """Adapter for OpenAI models."""

    def __init__(self, model_name: str = "gpt-4", api_key: str | None = None, **kwargs):
        """
        Initialize OpenAI model.

        Args:
            model_name: OpenAI model name (default: gpt-4)
            api_key: OpenAI API key (default: reads from OPENAI_API_KEY env var)
            **kwargs: Additional arguments
        """
        super().__init__(model_name, api_key, **kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        Generate response using OpenAI API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional OpenAI parameters

        Returns:
            Generated response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content

    def get_model_info(self) -> dict:
        """Get OpenAI model information."""
        return {"provider": "openai", "model_name": self.model_name, "api_version": "v1"}
