"""SGLang adapter for high-performance local LLM inference."""

from typing import Optional, Dict

from .base import BaseModel


class SGLangModel(BaseModel):
    """
    Adapter for SGLang - high-performance local inference engine.

    SGLang is optimized for:
    - Multi-turn conversations (3-5x better cache hit rate)
    - Structured outputs (10x faster than alternatives)
    - High throughput (up to 5x faster than vLLM in complex workflows)

    Examples:
        - Local models: "meta-llama/Llama-3.1-70B-Instruct"
        - DeepSeek: "deepseek-ai/DeepSeek-V3"
        - Qwen: "Qwen/Qwen2.5-72B-Instruct"
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        host: str = "http://localhost",
        port: int = 30000,
        **kwargs,
    ):
        """
        Initialize SGLang model.

        Prerequisites:
        1. Start SGLang server:
           python -m sglang.launch_server --model-path meta-llama/Llama-3.1-70B-Instruct --port 30000

        2. Or use Docker:
           docker run --gpus all -p 30000:30000 lmsysorg/sglang:latest \\
               python -m sglang.launch_server --model-path meta-llama/Llama-3.1-70B-Instruct

        Args:
            model_name: Model path or HuggingFace model ID
            api_key: Optional API key (not typically needed for local)
            host: SGLang server host
            port: SGLang server port
            **kwargs: Additional arguments
        """
        super().__init__(model_name, api_key, **kwargs)
        self.host = host
        self.port = port
        self.base_url = f"{host}:{port}"

        try:
            import requests

            self.requests = requests
        except ImportError:
            raise ImportError("requests package not installed. Install with: pip install requests")

        # Check if server is running
        try:
            response = self.requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code != 200:
                raise ConnectionError(f"SGLang server not healthy: {response.text}")
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to SGLang server at {self.base_url}. "
                f"Make sure the server is running. Error: {e}"
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
        Generate response using SGLang server.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional SGLang parameters

        Returns:
            Generated response
        """
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Make request to SGLang server
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            **kwargs,
        }

        try:
            response = self.requests.post(
                f"{self.base_url}/v1/chat/completions", json=payload, timeout=120
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except self.requests.exceptions.Timeout:
            raise TimeoutError(f"SGLang request timed out after 120s")
        except self.requests.exceptions.RequestException as e:
            raise RuntimeError(f"SGLang generation failed: {e}")

    def get_model_info(self) -> Dict:
        """Get SGLang model information."""
        try:
            response = self.requests.get(f"{self.base_url}/get_model_info", timeout=5)
            server_info = response.json() if response.status_code == 200 else {}
        except:
            server_info = {}

        return {
            "provider": "sglang",
            "model_name": self.model_name,
            "base_url": self.base_url,
            "server_info": server_info,
            "features": {
                "radix_attention": True,
                "structured_outputs": True,
                "multi_turn_optimized": True,
            },
        }
