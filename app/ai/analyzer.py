"""Structured OpenAI contract analysis."""

from __future__ import annotations

import json

from app.ai.client import create_client, current_model
from app.ai.prompts import ANALYSIS_SYSTEM, ANALYSIS_USER, analysis_json_schema
from app.document_processing.extractor import split_for_model
from app.models.types import AnalysisResult


def analyze_contract(document_text: str, category: str = "legal") -> AnalysisResult:
    chunks = split_for_model(document_text)
    if len(chunks) == 1:
        chunk_note = "The full extracted document is included below."
        combined = chunks[0]
    else:
        chunk_note = (
            f"This contract was split into {len(chunks)} sections so nothing is silently truncated. "
            "Analyze all sections together. If a later section conflicts with an earlier one, note it."
        )
        combined = "\n\n===== NEXT SECTION =====\n\n".join(
            f"[Section {i} of {len(chunks)}]\n{chunk}" for i, chunk in enumerate(chunks, start=1)
        )

    client = create_client()
    model = current_model()
    user_prompt = ANALYSIS_USER.format(
        category=category,
        document_text=combined,
        chunk_note=chunk_note,
    )

    try:
        response = client.responses.create(
            model=model,
            temperature=0.2,
            instructions=ANALYSIS_SYSTEM,
            input=user_prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "contract_analysis",
                    "strict": True,
                    "schema": analysis_json_schema(),
                }
            },
        )
        payload = json.loads(response.output_text)
    except Exception:
        # Fallback for accounts / models that do not support responses + json_schema.
        payload = _chat_completions_fallback(client, model, user_prompt)

    result = AnalysisResult.from_dict(payload)
    result.model = model
    return result


def _chat_completions_fallback(client, model: str, user_prompt: str) -> dict:
    completion = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM},
            {
                "role": "user",
                "content": user_prompt
                + "\n\nRespond with a single JSON object matching the described fields.",
            },
        ],
    )
    content = completion.choices[0].message.content or "{}"
    return json.loads(content)
