"""Extract text from PDF, DOCX, and plain-text contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config import SUPPORTED_EXTENSIONS


@dataclass
class PageText:
    page_number: int
    text: str
    heading: str = ""
    ocr_used: bool = False
    failed: bool = False
    note: str = ""


@dataclass
class ExtractedDocument:
    path: Path
    file_type: str
    pages: list[PageText] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        blocks = []
        for page in self.pages:
            label = f"--- Page {page.page_number}"
            if page.heading:
                label += f" | {page.heading}"
            if page.failed:
                label += " | NOT PROCESSED"
            label += " ---"
            body = page.text.strip() if page.text.strip() else page.note or "[No text extracted]"
            blocks.append(f"{label}\n{body}")
        return "\n\n".join(blocks)

    @property
    def page_count(self) -> int:
        return len(self.pages)


def extract_document(path: str | Path) -> ExtractedDocument:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Please upload a PDF, Word, or text document."
        )
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix == ".docx":
        return _extract_docx(file_path)
    if suffix == ".doc":
        raise ValueError(
            "Legacy .doc files are not fully supported. Please save the contract as PDF or DOCX and try again."
        )
    return _extract_txt(file_path)


def _extract_txt(path: Path) -> ExtractedDocument:
    text = path.read_text(encoding="utf-8", errors="replace")
    return ExtractedDocument(
        path=path,
        file_type="txt",
        pages=[PageText(page_number=1, text=text)],
    )


def _extract_docx(path: Path) -> ExtractedDocument:
    from docx import Document

    document = Document(str(path))
    pages: list[PageText] = []
    current: list[str] = []
    heading = ""
    page_no = 1
    char_budget = 3500

    for para in document.paragraphs:
        style = (para.style.name or "").lower() if para.style else ""
        text = para.text.strip()
        if not text:
            continue
        if "heading" in style:
            if current:
                pages.append(
                    PageText(page_number=page_no, text="\n".join(current), heading=heading)
                )
                page_no += 1
                current = []
            heading = text
        current.append(text)
        if sum(len(x) for x in current) >= char_budget:
            pages.append(PageText(page_number=page_no, text="\n".join(current), heading=heading))
            page_no += 1
            current = []
    if current:
        pages.append(PageText(page_number=page_no, text="\n".join(current), heading=heading))
    if not pages:
        pages = [PageText(page_number=1, text="", failed=True, note="No paragraphs found in this Word document.")]
    return ExtractedDocument(path=path, file_type="docx", pages=pages)


def _extract_pdf(path: Path) -> ExtractedDocument:
    import fitz

    notes: list[str] = []
    pages: list[PageText] = []
    with fitz.open(str(path)) as pdf:
        for index, page in enumerate(pdf, start=1):
            text = (page.get_text("text") or "").strip()
            heading = _guess_heading(text)
            ocr_used = False
            failed = False
            note = ""
            if len(text) < 40:
                ocr_text, ocr_note = _ocr_page(page)
                if ocr_text:
                    text = ocr_text
                    ocr_used = True
                    notes.append(f"Page {index}: OCR was used because little selectable text was found.")
                else:
                    failed = len(text) == 0
                    note = ocr_note or "Little or no text could be extracted from this page."
                    notes.append(f"Page {index}: {note}")
            pages.append(
                PageText(
                    page_number=index,
                    text=text,
                    heading=heading,
                    ocr_used=ocr_used,
                    failed=failed,
                    note=note,
                )
            )
    return ExtractedDocument(path=path, file_type="pdf", pages=pages, notes=notes)


def _guess_heading(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if 8 <= len(cleaned) <= 90:
            return cleaned
    return ""


def _ocr_page(page) -> tuple[str, str]:
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except Exception:
        return "", "This page looks scanned. Install Tesseract OCR to enable scanned-PDF reading."

    try:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(image) or ""
        if not text.strip():
            return "", "OCR ran but did not find readable text on this page."
        return text.strip(), ""
    except Exception as exc:
        return "", f"OCR is unavailable ({exc}). Scanned pages may be incomplete."


def split_for_model(text: str, max_chars: int = 12000) -> list[str]:
    """Split long contracts into overlapping sections without silent truncation."""
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    overlap = 800
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            break_at = text.rfind("\n--- Page", start + max_chars // 2, end)
            if break_at > start:
                end = break_at
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks
