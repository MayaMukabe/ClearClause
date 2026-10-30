# ClearClause AI

**Understand Your Health Insurance.**

ClearClause AI is a one-page web app that helps people read health insurance paperwork in plain language. You upload an explanation of benefits (EOB), denial letter, bill, coverage notice, or similar document. The app extracts the text, asks an AI to explain it, flags high / medium / low risk items, and can draft a **claim** or **appeal** letter.

This is an informational student project. It does **not** provide legal, medical, or insurance advice. Always check the original document before you send anything to an insurer.

Live on your computer: **http://127.0.0.1:8000** (only while the app is running).

---

## What is going on

| Piece | What it does |
| --- | --- |
| Browser page (`web/`) | The screen you see: upload, analyze, summary, risks, claim/appeal |
| Python server (`web/app.py`) | Receives the file, extracts text, calls the AI, returns results |
| Document extraction | Reads PDF, Word, images, or pasted text (OCR for scans when Tesseract is installed) |
| AI | By default a **free local model** via [Ollama](https://ollama.com) (Llama 3.2). OpenAI is optional if you have credits |
| SQLite | Saves analysis on this computer so claim/appeal can use the same document |

**Default AI is local.** Document text stays on your Mac when `AI_PROVIDER=ollama`. If you switch to OpenAI, extracted text is sent to OpenAI.

GitHub holds the **source code**. It does **not** run the app for visitors.

---

## How to use it (on this computer)

### 1. One-time setup

You need Python 3.10+ and the free Ollama app.

```bash
cd "ClearClause"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Install and start Ollama, then download the model (about 2 GB, once):

```bash
# If Ollama is not installed: https://ollama.com/download
ollama serve
ollama pull llama3.2:3b
```

`.env` should look like:

```
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
```

Keep `.env` off GitHub. It is already in `.gitignore`.

### 2. Start the app (two terminals)

**Terminal A — local AI**

```bash
ollama serve
```

**Terminal B — website**

```bash
source .venv/bin/activate
python main.py
```

Open **http://127.0.0.1:8000** in Chrome or Safari. Leave both terminals running.

### 3. Analyze a document

1. Click **Choose File** (PDF, Word, or image) or **Paste text**.
2. Click **✦ Analyze Document**.
3. Accept the privacy notice.
4. Wait. A short page may take under a minute; a ~20-page contract on the local model often takes **2–6 minutes**.
5. Read **Document Summary**, the risk tiles, and **Plain-Language Explanation**.
6. Optionally click **Create a Claim** or **Create an Appeal**, then copy the draft and edit it yourself.

A sample file is `tests/sample_eob.txt`.

### Optional: OpenAI instead of Ollama

Only if you have API credits. In `.env`:

```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

Never commit that key. Never paste it into GitHub.

---

## Can GitHub give me a public link?

**No.** GitHub (and GitHub Pages) is for storing and showing **code**. This project is a Python server plus a local AI. GitHub Pages only hosts static files (HTML/CSS/JS). It cannot run FastAPI, extract PDFs, or run Ollama.

Pushing to GitHub is still useful so teammates can **clone the repo and run it locally**. It does not create a website like `https://yourname.github.io/clearclause` that analyzes documents.

### Ways to get a link other people can open

| Option | What you get | Good for |
| --- | --- | --- |
| **http://127.0.0.1:8000** | Only you, on this Mac | Everyday testing |
| **ngrok** (or Cloudflare Tunnel) | A temporary `https://….ngrok.app` URL that points at your laptop | A demo for class, as long as your Mac stays on |
| **Render / Railway / Fly.io** | A real public site | Sharing 24/7, but you must use a **cloud AI** (OpenAI), not Ollama on your laptop |

**GitHub is the repo. A host like Render (or a tunnel like ngrok) is the public link.**

### Quick demo link with ngrok (laptop must stay on)

1. Start Ollama and `python main.py` as above.
2. Install [ngrok](https://ngrok.com/download), then:

```bash
ngrok http 8000
```

3. Share the `https://…` URL ngrok prints. Anyone with that URL can use your app until you close ngrok or shut the laptop.

Health documents will pass through your computer. Only share with people you trust, and stop ngrok when the demo ends.

### A lasting public website

You would deploy this FastAPI app to a host (Render, Railway, Fly.io), set environment variables there, and use **OpenAI** (or another hosted API). Ollama will not run on GitHub Pages and usually will not run on a free static host.

If you do that:

- Put the API key in the host’s secret settings, not in the repo.
- Remember you are sending insurance text to that AI provider.
- Expect usage costs if traffic grows.

---

## Project layout

```
main.py                 Starts the web server
web/                    Browser UI and API
app/ai/                 Prompts, analysis, claim/appeal drafts
app/document_processing Extracts PDF / Word / images / text
app/database/           Local SQLite history
app/services/           Ties extraction + AI together
tests/                  Sample EOB and unit tests
```

---

## Disclaimer

ClearClause AI is an informational tool designed to help individuals better understand health insurance documents. It does not provide legal, medical, or insurance advice and does not replace a licensed professional or your insurer. AI-generated explanations, risk notes, claims, and appeals may contain errors or omissions. Confirm every detail against the original document before submitting anything to an insurer.
