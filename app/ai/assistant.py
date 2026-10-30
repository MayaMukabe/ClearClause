"""Document-grounded chat assistant."""

from __future__ import annotations

from app.ai.client import create_client, current_model
from app.ai.prompts import ASSISTANT_SYSTEM


def answer_question(
    *,
    document_text: str,
    question: str,
    history: list[dict[str, str]],
    document_name: str,
    category: str,
) -> str:
    client = create_client()
    model = current_model()
    excerpt = document_text
    if len(excerpt) > 40000:
        excerpt = excerpt[:40000] + "\n\n[Document continues; ask about a specific page if needed.]"

    messages = [
        {"role": "system", "content": ASSISTANT_SYSTEM},
        {
            "role": "system",
            "content": (
                f"Current document: {document_name}\nCategory: {category}\n\n"
                f"Extracted text:\n{excerpt}"
            ),
        },
    ]
    for item in history[-12:]:
        role = item.get("role")
        if role in {"user", "assistant"}:
            messages.append({"role": role, "content": item.get("content", "")})
    messages.append({"role": "user", "content": question})

    try:
        response = client.responses.create(
            model=model,
            temperature=0.3,
            input=messages,
        )
        return (response.output_text or "").strip()
    except Exception:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=messages,
        )
        return (completion.choices[0].message.content or "").strip()
