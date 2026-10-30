"""AI client factory. Supports OpenAI (paid) and Ollama (free, local)."""

from __future__ import annotations

from openai import OpenAI

from app.config import (
    get_api_key,
    get_model,
    get_ollama_model,
    get_provider,
    ollama_base_url,
)


class MissingAPIKeyError(RuntimeError):
    pass


class LocalAIUnavailableError(RuntimeError):
    pass


def create_client(provider: str | None = None) -> OpenAI:
    provider = (provider or get_provider()).lower()
    if provider == "ollama":
        return OpenAI(base_url=ollama_base_url(), api_key="ollama")
    key = get_api_key()
    if not key:
        raise MissingAPIKeyError(
            "No OpenAI API key is configured. Use the free local model (Ollama) instead."
        )
    return OpenAI(api_key=key)


def current_model(provider: str | None = None) -> str:
    provider = (provider or get_provider()).lower()
    if provider == "ollama":
        return get_ollama_model()
    return get_model()


def uses_openai_responses(provider: str | None = None) -> bool:
    return (provider or get_provider()).lower() == "openai"
