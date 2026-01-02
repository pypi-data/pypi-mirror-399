"""LLM Provider for TurnWise SDK.

Simplified OpenRouter integration for running evaluations locally.
"""
import logging
from typing import Any, Dict, List, Optional

import httpx
import tiktoken
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class OpenRouterProvider:
    """OpenRouter LLM provider for evaluation."""

    BASE_URL = "https://openrouter.ai/api/v1"

    # Default context sizes for common models (fallback if not queried)
    MODEL_CONTEXT_SIZES = {
        "openai/gpt-4o": 128000,
        "openai/gpt-4o-mini": 128000,
        "openai/gpt-4-turbo": 128000,
        "openai/gpt-4": 8192,
        "openai/gpt-3.5-turbo": 16385,
        "anthropic/claude-3-5-sonnet": 200000,
        "anthropic/claude-3-opus": 200000,
        "anthropic/claude-3-sonnet": 200000,
        "anthropic/claude-3-haiku": 200000,
        "google/gemini-pro-1.5": 1000000,
        "google/gemini-flash-1.5": 1000000,
    }

    DEFAULT_CONTEXT_SIZE = 32000

    def __init__(self, api_key: str):
        """
        Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required")

        self.api_key = api_key
        self._models_cache: Optional[List[Dict[str, Any]]] = None
        self._encoding = tiktoken.get_encoding("cl100k_base")

    def get_llm(
        self,
        model_name: str = "openai/gpt-4o-mini",
        temperature: float = 0,
    ) -> ChatOpenAI:
        """
        Get configured LLM instance.

        Args:
            model_name: OpenRouter model name (e.g., "openai/gpt-4o-mini")
            temperature: Model temperature (0-2)

        Returns:
            Configured ChatOpenAI instance for OpenRouter
        """
        return ChatOpenAI(
            model=model_name,
            api_key=self.api_key,
            base_url=self.BASE_URL,
            temperature=temperature,
        )

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self._encoding.encode(text))

    def get_context_size(self, model_name: str) -> int:
        """
        Get context size for a model.

        Args:
            model_name: Model name

        Returns:
            Context size in tokens
        """
        # Check known models first
        if model_name in self.MODEL_CONTEXT_SIZES:
            return self.MODEL_CONTEXT_SIZES[model_name]

        # Try to get from API cache
        if self._models_cache:
            for model in self._models_cache:
                if model.get("id") == model_name:
                    top_provider = model.get("top_provider", {})
                    if isinstance(top_provider, dict):
                        context = top_provider.get("context_length")
                        if context:
                            return int(context)

        return self.DEFAULT_CONTEXT_SIZE

    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from OpenRouter.

        Returns:
            List of model dictionaries
        """
        if self._models_cache is not None:
            return self._models_cache

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            models = response.json().get("data", [])
            self._models_cache = models
            return models

    def get_models_sync(self) -> List[Dict[str, Any]]:
        """
        Get list of available models (synchronous version).

        Returns:
            List of model dictionaries
        """
        if self._models_cache is not None:
            return self._models_cache

        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            models = response.json().get("data", [])
            self._models_cache = models
            return models

    def get_model_pricing(self, model_name: str) -> Optional[Dict[str, float]]:
        """
        Get pricing for a specific model.

        Args:
            model_name: Model name (e.g., "openai/gpt-4o-mini")

        Returns:
            Dict with 'prompt' and 'completion' prices per token, or None
        """
        try:
            models = self.get_models_sync()
            for model in models:
                if model.get("id") == model_name:
                    pricing = model.get("pricing", {})
                    if pricing:
                        return {
                            "prompt": float(pricing.get("prompt", 0)),
                            "completion": float(pricing.get("completion", 0)),
                        }
            return None
        except Exception as e:
            logger.warning(f"Failed to get model pricing for {model_name}: {e}")
            return None
