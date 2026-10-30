# ClearClause AI

**Understand Before You Sign.**

ClearClause AI is a local desktop app that helps people understand contracts, agreements, and other dense documents. Upload a file, and the app extracts the text on your computer, then uses the OpenAI API to explain clauses, flag potential risks, and answer questions in plain language.

This is an informational tool. It does not provide legal advice.

## Features

- Upload PDF, Word (DOCX), and text documents, including drag-and-drop
- Local text extraction with optional OCR for scanned PDFs (if Tesseract is installed)
- Structured contract analysis: overview, clauses, risk levels, and a **Before You Sign** section
- Plain-language translator for selected clauses
- Document-grounded AI assistant with follow-up questions
- SQLite history so analyses remain after you quit
- Privacy notice before text is sent to OpenAI

## Requirements

- Python 3.10 or newer
- An [OpenAI API key](https://platform.openai.com/api-keys)
- Optional: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for scanned PDFs

## Setup

```bash
cd "ClearClause"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

You can also paste the key later in **Settings**.

## Run

```bash
python main.py
```

## Using the app

1. Start on the **Dashboard**, which follows the ClearClause home layout.
2. Choose **Legal Document** or **Health Document**.
3. Upload a contract (try `tests/sample_lease.txt`).
4. Confirm the privacy notice, then analyze.
5. Review risks, key findings, and **Before You Sign**.
6. Ask follow-up questions on the dashboard or in **AI Assistant**.
7. Reopen past work from **My Documents**.

## Privacy

Uploaded files are copied into the local application data folder. When you request analysis or chat, extracted text is sent to OpenAI. OpenAI’s API data policies apply. Delete documents from **My Documents** to remove the stored file, analysis, and chat history from this computer.

## Legal disclaimer

ClearClause AI is an informational tool designed to help individuals better understand legal documents. It does not provide legal advice and does not replace consultation with a licensed attorney. AI-generated explanations, summaries, and risk assessments may contain errors or omissions. Users should consult a qualified legal professional before making significant legal or financial decisions.

## Project layout

```
main.py
app/
  ui/                 Desktop interface
  services/           Application workflow
  ai/                 OpenAI analysis and assistant
  document_processing Text extraction and sectioning
  database/           SQLite storage
  models/             Shared data types
assets/images/        Unsplash photos used in the backdrop
tests/
```

Photos in `assets/images` are downloaded from [Unsplash](https://unsplash.com).
