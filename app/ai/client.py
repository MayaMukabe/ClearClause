"""OpenAI client factory. API keys are never logged."""

from __future__ import annotations

from openai import OpenAI

from app.config import get_api_key, get_model


class MissingAPIKeyError(RuntimeError):
    pass


def create_client() -> OpenAI:
    key = get_api_key()
    if not key:
        raise MissingAPIKeyError(
            "Add your OpenAI API key in Settings before analyzing a document."
        )
    return OpenAI(api_key=key)


def current_model() -> str:
    return get_model()
