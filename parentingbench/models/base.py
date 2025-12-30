"""Base class for LLM providers."""

from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model_name: str, api_key: str | None = None, **kwargs):
        """
        Initialize the model.

        Args:
            model_name: Name/identifier of the model
            api_key: API key for the provider (if required)
            **kwargs: Additional provider-specific arguments
        """
        self.model_name = model_name
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        """
        Generate a response to the given prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        """
        Get information about the model.

        Returns:
            Dictionary with model metadata
        """
        pass
