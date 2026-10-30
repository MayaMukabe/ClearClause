"""Application configuration and paths."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

LEGAL_DISCLAIMER = (
    "ClearClause AI is an informational tool designed to help individuals "
    "better understand legal documents. It does not provide legal advice and "
    "does not replace consultation with a licensed attorney. AI-generated "
    "explanations, summaries, and risk assessments may contain errors or "
    "omissions. Users should consult a qualified legal professional before "
    "making significant legal or financial decisions."
)

PRIVACY_NOTICE = (
    "When you analyze a document, extracted text from that file is sent to "
    "OpenAI so the AI can generate summaries, risk assessments, and answers. "
    "Uploaded files stay on this computer by default. OpenAI's API data "
    "policies apply to any text submitted for analysis. Do not analyze "
    "documents you are not authorized to share with a third-party AI service."
)

SUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-4.1",
]

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


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


def env_file_path() -> Path:
    local = project_root() / ".env"
    if local.exists():
        return local
    return user_data_dir() / ".env"


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


def save_api_settings(api_key: str, model: str) -> Path:
    """Persist API settings to a local .env file (not logged)."""
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
