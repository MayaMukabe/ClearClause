# ClearClause AI

**Understand Your Health Insurance.**

ClearClause AI is a one-page website you run on your computer. You upload a health insurance document (or paste the text). The app explains it in plain language, flags high / medium / low risk items, and can draft a claim or appeal letter.

This is **not** legal, medical, or insurance advice. Always check the original document before you send anything to an insurer.

---

## First-time setup (do this once)

### Step 1 — Get the code

1. Open [https://github.com/MayaMukabe/ClearClause](https://github.com/MayaMukabe/ClearClause).
2. Click the green **Code** button → **Download ZIP**, or clone the repo if you use Git.
3. Unzip it and open the `ClearClause` folder in Terminal.

```bash
cd "ClearClause"
```

### Step 2 — Install Python packages

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows use:

```bash
.venv\Scripts\activate
```

### Step 3 — Create your private settings file

```bash
cp .env.example .env
```

You will put **your own** API key in `.env` in the next section. Never upload `.env` to GitHub.

---

## How to add your own OpenAI API key

Everyone who runs this project must use **their own** key. Do not use someone else’s key.

### Step 1 — Create a key on OpenAI

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) and sign in (or create an account).
2. Click **Create new secret key**.
3. Copy the key. It starts with `sk-`. You will only see it once.
4. Add a little credit on OpenAI if the site says you are out of quota. A key with $0 balance will fail with “insufficient credits.”

### Step 2 — Paste the key into `.env`

1. In the project folder, open the file named **`.env`** in any text editor.
2. Make it look like this (use **your** key, not this example):

```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-paste-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

3. Save the file.
4. Do **not** put the key in `README.md`, GitHub, screenshots, or chat.

If the file already has `AI_PROVIDER=ollama`, change it to `openai` so the app uses your key.

### Step 3 — Restart the app

If the website is already running, stop it (Control+C in Terminal) and start it again so it loads the new key:

```bash
source .venv/bin/activate
python main.py
```

---

## How to open the website

1. In Terminal, make sure you are in the project folder and the virtual environment is on:

```bash
cd "ClearClause"
source .venv/bin/activate
python main.py
```

2. Open a browser and go to:

**http://127.0.0.1:8000**

3. Leave the Terminal window open. Closing it shuts the site off.

The site only works on **your** computer unless you later deploy it or use a tool like ngrok.

---

## How to use the interface (step by step)

You should see one page: **ClearClause AI — Understand Your Health Insurance.**

### 1. Add a document

Do **one** of these:

- Click **Choose File** and pick a PDF, Word file, image, or `.txt` file  
  **or**
- Drag the file onto the dashed **Upload Your Health Document** box  
  **or**
- Click **Paste text**, paste the document, then click **Analyze text** in that popup (this only stores the text; analysis still needs the button in step 2)

The file name should appear under the buttons. Nothing is sent to the AI yet.

### 2. Analyze

1. Click **✦ Analyze Document**.
2. Read the privacy notice.
3. Check **I understand and want to continue**.
4. Click **Continue**.
5. Wait. A short document may take under a minute. A long one (around 20 pages) can take several minutes, especially on a slower computer.

If you see a credits / quota error, your OpenAI account needs billing credit, or your key is missing from `.env`.

### 3. Read the results (same page)

- **Document Summary** (left): insurance provider, member name, service dates, claim number, document type.
- **AI Analysis** (right):
  - **High / Medium / Low Risk** tiles
  - **Plain-Language Explanation** of what the document means

### 4. Optional: create a letter

Only after a successful analysis:

1. Click **Create a Claim** to draft a letter asking the insurer to process/pay a claim  
  **or**
  click **Create an Appeal** to draft a letter asking them to review a denial or underpayment.
2. Read the draft. Edit anything that looks wrong.
3. Click **Copy letter**, then paste it into Word or email.
4. Click **Close**.

The app does **not** send the letter to the insurance company. You do that yourself after you check it.

### 5. Analyze another document

Choose or paste a new file, then click **✦ Analyze Document** again.

---

## Using the app for free (no OpenAI key)

If you do not want to pay OpenAI, you can run a model on your computer with [Ollama](https://ollama.com/download).

1. Install Ollama from that site.
2. In Terminal:

```bash
ollama serve
ollama pull llama3.2:3b
```

3. In `.env` put:

```
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
```

4. Keep `ollama serve` running in one Terminal, and `python main.py` in another.
5. Use the website the same way as above.

Local analysis is free but slower and less accurate than OpenAI.

---

## Sample file to try

`tests/sample_eob.txt` — open it, copy the text, use **Paste text**, then **✦ Analyze Document**.

---

## Public link / GitHub

GitHub only stores the **code**. It does **not** give you a public website.

- **You:** http://127.0.0.1:8000 while the app is running  
- **Temporary demo for others:** [ngrok](https://ngrok.com/download) → `ngrok http 8000` (your laptop must stay on)  
- **Always-on public site:** deploy to Render / Railway / Fly.io and put **your** `OPENAI_API_KEY` in that host’s secret settings, not in GitHub

---

## Disclaimer

ClearClause AI is an informational tool designed to help individuals better understand health insurance documents. It does not provide legal, medical, or insurance advice and does not replace a licensed professional or your insurer. AI-generated explanations, risk notes, claims, and appeals may contain errors or omissions. Confirm every detail against the original document before submitting anything to an insurer.
