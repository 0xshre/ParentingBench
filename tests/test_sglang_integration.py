"""
Tests for SGLang integration.

These tests verify the adapter works correctly without requiring a real SGLang server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from parentingbench.models.sglang_adapter import SGLangModel


def test_sglang_init_success():
    """Test SGLang model initialization with healthy server."""
    with patch('parentingbench.models.sglang_adapter.requests') as mock_requests:
        # Mock health check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        model = SGLangModel(
            model_name="meta-llama/Llama-3.1-70B-Instruct",
            host="http://localhost",
            port=30000
        )

        assert model.model_name == "meta-llama/Llama-3.1-70B-Instruct"
        assert model.base_url == "http://localhost:30000"

        # Verify health check was called
        mock_requests.get.assert_called_once()
        assert "/health" in str(mock_requests.get.call_args)


def test_sglang_init_server_not_running():
    """Test SGLang initialization when server is not running."""
    with patch('parentingbench.models.sglang_adapter.requests') as mock_requests:
        mock_requests.get.side_effect = Exception("Connection refused")

        with pytest.raises(ConnectionError, match="Cannot connect to SGLang server"):
            SGLangModel("meta-llama/Llama-3.1-70B-Instruct")


def test_sglang_generate():
    """Test SGLang generate method."""
    with patch('parentingbench.models.sglang_adapter.requests') as mock_requests:
        # Mock health check
        health_response = Mock()
        health_response.status_code = 200

        # Mock generation response
        gen_response = Mock()
        gen_response.status_code = 200
        gen_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response from SGLang"
                    }
                }
            ]
        }

        # Setup mock to return different responses for health vs generation
        mock_requests.get.return_value = health_response
        mock_requests.post.return_value = gen_response

        # Create model and generate
        model = SGLangModel("meta-llama/Llama-3.1-70B-Instruct")
        response = model.generate(
            prompt="Test prompt",
            system_prompt="System prompt",
            temperature=0.7,
            max_tokens=100
        )

        # Verify
        assert response == "Test response from SGLang"
        mock_requests.post.assert_called_once()

        # Check call arguments
        call_args = mock_requests.post.call_args
        assert "/v1/chat/completions" in call_args[0][0]

        payload = call_args[1]["json"]
        assert payload["temperature"] == 0.7
        assert payload["max_tokens"] == 100
        assert len(payload["messages"]) == 2  # system + user


def test_sglang_generate_timeout():
    """Test SGLang timeout handling."""
    with patch('parentingbench.models.sglang_adapter.requests') as mock_requests:
        # Mock health check
        health_response = Mock()
        health_response.status_code = 200
        mock_requests.get.return_value = health_response

        # Mock timeout on generation
        from requests.exceptions import Timeout
        mock_requests.post.side_effect = Timeout()

        model = SGLangModel("meta-llama/Llama-3.1-70B-Instruct")

        with pytest.raises(TimeoutError, match="SGLang request timed out"):
            model.generate(prompt="Test prompt")


def test_sglang_get_model_info():
    """Test getting SGLang model information."""
    with patch('parentingbench.models.sglang_adapter.requests') as mock_requests:
        # Mock health check
        health_response = Mock()
        health_response.status_code = 200

        # Mock model info response
        info_response = Mock()
        info_response.status_code = 200
        info_response.json.return_value = {
            "model_name": "meta-llama/Llama-3.1-70B-Instruct",
            "backend": "sglang",
            "version": "0.3.0"
        }

        mock_requests.get.side_effect = [health_response, info_response]

        model = SGLangModel("meta-llama/Llama-3.1-70B-Instruct")
        info = model.get_model_info()

        assert info["provider"] == "sglang"
        assert info["model_name"] == "meta-llama/Llama-3.1-70B-Instruct"
        assert info["features"]["radix_attention"] is True
        assert info["features"]["structured_outputs"] is True
        assert info["features"]["multi_turn_optimized"] is True


def test_sglang_missing_requests():
    """Test handling of missing requests package."""
    with patch('builtins.__import__', side_effect=ImportError):
        with pytest.raises(ImportError, match="requests package not installed"):
            # This should fail before even trying to connect
            with patch('parentingbench.models.sglang_adapter.requests', None):
                SGLangModel("test-model")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
