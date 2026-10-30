from __future__ import annotations


def preview_text(text: str, limit: int = 4000) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "\n\n… preview truncated for display. The full document is still used for analysis."
