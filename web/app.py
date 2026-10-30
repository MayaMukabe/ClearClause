"""FastAPI web app for ClearClause AI."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import (
    LEGAL_DISCLAIMER,
    PRIVACY_NOTICE,
    SUPPORTED_EXTENSIONS,
    ai_is_ready,
    assets_dir,
    get_provider,
    load_environment,
)
from app.services.document_service import DocumentService

load_environment()

WEB_DIR = Path(__file__).resolve().parent
service = DocumentService()

app = FastAPI(title="ClearClause AI", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.mount("/assets", StaticFiles(directory=assets_dir()), name="assets")


@app.get("/")
def home() -> FileResponse:
    return FileResponse(WEB_DIR / "templates" / "index.html")


@app.get("/api/meta")
def meta() -> dict:
    return {
        "disclaimer": LEGAL_DISCLAIMER,
        "privacy": PRIVACY_NOTICE,
        "has_api_key": ai_is_ready(),
        "provider": get_provider(),
    }


@app.post("/api/analyze")
async def analyze(
    privacy_accepted: str = Form(...),
    pasted_text: str = Form(""),
    file: UploadFile | None = File(None),
) -> dict:
    if privacy_accepted.lower() not in {"true", "1", "on", "yes"}:
        raise HTTPException(status_code=400, detail="Please accept the privacy notice to continue.")
    if not ai_is_ready():
        raise HTTPException(
            status_code=503,
            detail="No AI is configured. Install Ollama for a free local model, or add an OpenAI key.",
        )
    try:
        if file is not None and file.filename:
            suffix = Path(file.filename).suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail="Please upload a PDF, Word, image, or text file.",
                )
            data = await file.read()
            if not data:
                raise HTTPException(status_code=400, detail="The uploaded file was empty.")
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(data)
                tmp_path = Path(tmp.name)
            try:
                record = service.import_file(tmp_path)
                record.name = file.filename
            finally:
                tmp_path.unlink(missing_ok=True)
        elif pasted_text.strip():
            record = service.import_text(pasted_text.strip())
        else:
            raise HTTPException(status_code=400, detail="Choose a file or paste document text.")
        if record.id is None:
            raise HTTPException(status_code=500, detail="Could not save the document.")
        result = service.analyze(record.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "document_id": record.id,
        "name": file.filename if file and file.filename else record.name,
        "overview": {
            "insurance_provider": result.overview.insurance_provider,
            "member_name": result.overview.member_name,
            "service_dates": result.overview.service_dates,
            "claim_number": result.overview.claim_number,
            "document_type": result.overview.document_type,
        },
        "risk_counts": result.risk_counts,
        "findings": [
            {
                "name": item.name,
                "risk_level": item.risk_level,
                "simple_explanation": item.simple_explanation,
            }
            for item in result.findings
        ],
        "plain_language": result.plain_language,
        "processing_notes": result.processing_notes,
    }


@app.post("/api/letter")
async def letter(document_id: int = Form(...), kind: str = Form(...)) -> dict:
    if kind not in {"claim", "appeal"}:
        raise HTTPException(status_code=400, detail="Choose claim or appeal.")
    if not ai_is_ready():
        raise HTTPException(
            status_code=503,
            detail="No AI is configured. Install Ollama for a free local model, or add an OpenAI key.",
        )
    try:
        text = service.draft_letter(document_id, kind)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"letter": text, "kind": kind}


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run("web.app:app", host=host, port=port, reload=False)
