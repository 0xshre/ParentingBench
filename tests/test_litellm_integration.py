"""
Tests for LiteLLM integration.

These tests verify the adapter works correctly without requiring real API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from parentingbench.models.litellm_adapter import LiteLLMModel


def test_litellm_init():
    """Test LiteLLM model initialization."""
    with patch('parentingbench.models.litellm_adapter.litellm'):
        model = LiteLLMModel("gpt-4")
        assert model.model_name == "gpt-4"
        assert model._detect_provider("gpt-4") == "openai"


def test_litellm_provider_detection():
    """Test provider detection from model names."""
    with patch('parentingbench.models.litellm_adapter.litellm'):
        model = LiteLLMModel("test-model")

        assert model._detect_provider("gpt-4") == "openai"
        assert model._detect_provider("gpt-3.5-turbo") == "openai"
        assert model._detect_provider("claude-3-5-sonnet-20241022") == "anthropic"
        assert model._detect_provider("claude-3-opus") == "anthropic"
        assert model._detect_provider("gemini/gemini-pro") == "gemini"
        assert model._detect_provider("ollama/llama3.2") == "ollama"
        assert model._detect_provider("unknown-model") == "unknown"


def test_litellm_generate():
    """Test LiteLLM generate method."""
    with patch('parentingbench.models.litellm_adapter.litellm') as mock_litellm:
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"

        mock_litellm.completion.return_value = mock_response

        # Create model and generate
        model = LiteLLMModel("gpt-4")
        response = model.generate(
            prompt="Test prompt",
            system_prompt="System prompt",
            temperature=0.7,
            max_tokens=100
        )

        # Verify
        assert response == "Test response"
        mock_litellm.completion.assert_called_once()

        # Check call arguments
        call_args = mock_litellm.completion.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["max_tokens"] == 100
        assert len(call_args[1]["messages"]) == 2  # system + user


def test_litellm_generate_without_system_prompt():
    """Test LiteLLM generate without system prompt."""
    with patch('parentingbench.models.litellm_adapter.litellm') as mock_litellm:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"

        mock_litellm.completion.return_value = mock_response

        model = LiteLLMModel("gpt-4")
        response = model.generate(prompt="Test prompt")

        # Verify only user message
        call_args = mock_litellm.completion.call_args
        assert len(call_args[1]["messages"]) == 1  # only user


def test_litellm_get_model_info():
    """Test getting model information."""
    with patch('parentingbench.models.litellm_adapter.litellm'):
        model = LiteLLMModel("claude-3-5-sonnet-20241022")
        info = model.get_model_info()

        assert info["provider"] == "litellm:anthropic"
        assert info["model_name"] == "claude-3-5-sonnet-20241022"
        assert info["supports_streaming"] is True
        assert info["supports_function_calling"] is True


def test_litellm_error_handling():
    """Test error handling in LiteLLM."""
    with patch('parentingbench.models.litellm_adapter.litellm') as mock_litellm:
        mock_litellm.completion.side_effect = Exception("API Error")

        model = LiteLLMModel("gpt-4")

        with pytest.raises(RuntimeError, match="LiteLLM generation failed"):
            model.generate(prompt="Test prompt")


def test_litellm_missing_import():
    """Test handling of missing litellm package."""
    with patch('parentingbench.models.litellm_adapter.litellm', None):
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ImportError, match="litellm package not installed"):
                LiteLLMModel("gpt-4")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
