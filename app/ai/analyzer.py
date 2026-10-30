"""Structured analysis of health insurance documents."""

from __future__ import annotations

import json

from app.ai.client import create_client, current_model, uses_openai_responses
from app.ai.json_util import parse_json_content
from app.ai.prompts import ANALYSIS_SYSTEM, ANALYSIS_USER, analysis_json_schema
from app.config import get_provider
from app.document_processing.extractor import split_for_model
from app.models.types import AnalysisResult


def analyze_document(document_text: str) -> AnalysisResult:
    chunks = split_for_model(document_text)
    if len(chunks) == 1:
        chunk_note = "The full extracted document is included."
        combined = chunks[0]
    else:
        chunk_note = (
            f"This document was split into {len(chunks)} sections so nothing is silently truncated. "
            "Use every section."
        )
        combined = "\n\n===== NEXT SECTION =====\n\n".join(
            f"[Section {i} of {len(chunks)}]\n{chunk}" for i, chunk in enumerate(chunks, start=1)
        )

    user_prompt = ANALYSIS_USER.format(document_text=combined, chunk_note=chunk_note)
    provider = get_provider()
    if provider == "auto":
        try:
            payload, model = _run_analysis("openai", user_prompt)
        except Exception:
            payload, model = _run_analysis("ollama", user_prompt)
    else:
        payload, model = _run_analysis(provider, user_prompt)

    result = AnalysisResult.from_dict(payload)
    result.model = model
    return result


def _run_analysis(provider: str, user_prompt: str) -> tuple[dict, str]:
    client = create_client(provider)
    model = current_model(provider)
    if uses_openai_responses(provider):
        try:
            response = client.responses.create(
                model=model,
                temperature=0.2,
                instructions=ANALYSIS_SYSTEM,
                input=user_prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "health_document_analysis",
                        "strict": True,
                        "schema": analysis_json_schema(),
                    }
                },
            )
            return json.loads(response.output_text), model
        except Exception:
            pass
    return _chat_json(client, model, user_prompt), model


def _chat_json(client, model: str, user_prompt: str) -> dict:
    kwargs = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": ANALYSIS_SYSTEM},
            {
                "role": "user",
                "content": user_prompt
                + "\n\nRespond with a single JSON object matching the described fields. No markdown.",
            },
        ],
    }
    try:
        completion = client.chat.completions.create(response_format={"type": "json_object"}, **kwargs)
    except Exception:
        completion = client.chat.completions.create(**kwargs)
    return parse_json_content(completion.choices[0].message.content or "{}")
