"""
Basic tests for model adapters (no external dependencies required).

These tests verify the adapter interfaces without requiring actual API calls or libraries.
"""

import pytest
from parentingbench.models.base import BaseModel


def test_base_model_interface():
    """Test that BaseModel defines the required interface."""

    # BaseModel is abstract, so we create a minimal implementation
    class TestModel(BaseModel):
        def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2000, **kwargs):
            return "test response"

        def get_model_info(self):
            return {"provider": "test", "model_name": self.model_name}

    model = TestModel(model_name="test-model")
    assert model.model_name == "test-model"

    response = model.generate("test prompt")
    assert response == "test response"

    info = model.get_model_info()
    assert info["provider"] == "test"
    assert info["model_name"] == "test-model"


def test_litellm_adapter_exists():
    """Test that LiteLLM adapter module exists and has correct structure."""
    try:
        from parentingbench.models.litellm_adapter import LiteLLMModel
        from parentingbench.models.base import BaseModel

        # Verify it's a subclass of BaseModel
        assert issubclass(LiteLLMModel, BaseModel)

        # Verify required methods exist
        assert hasattr(LiteLLMModel, "generate")
        assert hasattr(LiteLLMModel, "get_model_info")
        assert hasattr(LiteLLMModel, "_detect_provider")

        print("✓ LiteLLMModel has correct structure")

    except ImportError as e:
        pytest.fail(f"Failed to import LiteLLMModel: {e}")


def test_sglang_adapter_exists():
    """Test that SGLang adapter module exists and has correct structure."""
    try:
        from parentingbench.models.sglang_adapter import SGLangModel
        from parentingbench.models.base import BaseModel

        # Verify it's a subclass of BaseModel
        assert issubclass(SGLangModel, BaseModel)

        # Verify required methods exist
        assert hasattr(SGLangModel, "generate")
        assert hasattr(SGLangModel, "get_model_info")

        print("✓ SGLangModel has correct structure")

    except ImportError as e:
        pytest.fail(f"Failed to import SGLangModel: {e}")


def test_all_adapters_importable():
    """Test that all adapters can be imported from models package."""
    try:
        from parentingbench.models import (
            BaseModel,
            OpenAIModel,
            AnthropicModel,
            LiteLLMModel,
            SGLangModel,
        )

        adapters = [OpenAIModel, AnthropicModel, LiteLLMModel, SGLangModel]

        for adapter in adapters:
            assert issubclass(
                adapter, BaseModel
            ), f"{adapter.__name__} should inherit from BaseModel"

        print(f"✓ All {len(adapters)} adapters importable and inherit from BaseModel")

    except ImportError as e:
        pytest.fail(f"Failed to import adapters: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
