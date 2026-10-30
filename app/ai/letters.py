"""Draft insurance claim and appeal letters from the current document."""

from __future__ import annotations

import json

from app.ai.client import create_client, current_model, uses_openai_responses
from app.ai.prompts import APPEAL_USER, CLAIM_USER, LETTER_SYSTEM
from app.config import get_provider
from app.models.types import AnalysisResult


def draft_letter(
    *,
    kind: str,
    document_name: str,
    document_text: str,
    analysis: AnalysisResult | None,
) -> str:
    if kind not in {"claim", "appeal"}:
        raise ValueError("Letter type must be claim or appeal.")
    excerpt = document_text if len(document_text) <= 35000 else document_text[:35000] + "\n[truncated for length]"
    analysis_json = json.dumps(analysis.to_dict() if analysis else {}, indent=2)
    template = CLAIM_USER if kind == "claim" else APPEAL_USER
    user_prompt = template.format(
        document_name=document_name,
        document_text=excerpt,
        analysis_json=analysis_json,
    )
    provider = get_provider()
    if provider == "auto":
        try:
            return _run_letter("openai", user_prompt)
        except Exception:
            return _run_letter("ollama", user_prompt)
    return _run_letter(provider, user_prompt)


def _run_letter(provider: str, user_prompt: str) -> str:
    client = create_client(provider)
    model = current_model(provider)
    if uses_openai_responses(provider):
        try:
            response = client.responses.create(
                model=model,
                temperature=0.3,
                instructions=LETTER_SYSTEM,
                input=user_prompt,
            )
            return (response.output_text or "").strip()
        except Exception:
            pass
    completion = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {"role": "system", "content": LETTER_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (completion.choices[0].message.content or "").strip()
