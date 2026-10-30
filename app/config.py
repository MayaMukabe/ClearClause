"""Application configuration and paths."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

LEGAL_DISCLAIMER = (
    "ClearClause AI is an informational tool designed to help individuals "
    "better understand health insurance documents. It does not provide legal, "
    "medical, or insurance advice and does not replace a licensed professional "
    "or your insurer. AI-generated explanations, risk notes, claims, and appeals "
    "may contain errors or omissions. Confirm every detail against the original "
    "document before submitting anything to an insurer."
)

PRIVACY_NOTICE = (
    "When you analyze a document, extracted or pasted text is sent to the "
    "selected AI. With the free local option (Ollama), text stays on this "
    "computer. If OpenAI is selected, text is sent to OpenAI and their API "
    "data policies apply. Do not upload documents you are not authorized to share."
)

SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-4.1",
]

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".tif",
    ".tiff",
}


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def assets_dir() -> Path:
    return project_root() / "assets"


def images_dir() -> Path:
    return assets_dir() / "images"


def user_data_dir() -> Path:
    if sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "ClearClauseAI"
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA", str(Path.home()))
        path = Path(base) / "ClearClauseAI"
    else:
        path = Path.home() / ".local" / "share" / "ClearClauseAI"
    path.mkdir(parents=True, exist_ok=True)
    return path


def documents_dir() -> Path:
    path = user_data_dir() / "documents"
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_path() -> Path:
    return user_data_dir() / "clearclause.db"


def load_environment() -> None:
    load_dotenv(project_root() / ".env")
    load_dotenv(user_data_dir() / ".env", override=False)


def get_api_key() -> str:
    load_environment()
    return os.environ.get("OPENAI_API_KEY", "").strip()


def get_model() -> str:
    load_environment()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
    return model or "gpt-4o-mini"


def get_provider() -> str:
    """openai, ollama, or auto (OpenAI first, then free local Ollama)."""
    load_environment()
    value = os.environ.get("AI_PROVIDER", "ollama").strip().lower()
    return value or "ollama"


def get_ollama_model() -> str:
    load_environment()
    return os.environ.get("OLLAMA_MODEL", "llama3.2:3b").strip() or "llama3.2:3b"


def ollama_base_url() -> str:
    load_environment()
    return os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1").strip()


def ai_is_ready() -> bool:
    provider = get_provider()
    if provider == "openai":
        return bool(get_api_key())
    if provider == "ollama":
        return True
    return True


def save_api_settings(api_key: str, model: str) -> Path:
    target = project_root() / ".env"
    existing = ""
    if target.exists():
        existing = target.read_text(encoding="utf-8")
    lines = []
    wrote_key = False
    wrote_model = False
    for line in existing.splitlines():
        if line.startswith("OPENAI_API_KEY="):
            lines.append(f"OPENAI_API_KEY={api_key.strip()}")
            wrote_key = True
        elif line.startswith("OPENAI_MODEL="):
            lines.append(f"OPENAI_MODEL={model.strip()}")
            wrote_model = True
        else:
            lines.append(line)
    if not wrote_key:
        lines.append(f"OPENAI_API_KEY={api_key.strip()}")
    if not wrote_model:
        lines.append(f"OPENAI_MODEL={model.strip()}")
    target.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    os.environ["OPENAI_API_KEY"] = api_key.strip()
    os.environ["OPENAI_MODEL"] = model.strip()
    return target
