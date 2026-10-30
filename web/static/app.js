const state = {
  documentId: null,
  pending: null,
  meta: {},
  file: null,
  pastedText: "",
};

const $ = (id) => document.getElementById(id);

function _error(data) {
  const detail = data && data.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || item).join(" ");
  return "";
}

async function loadMeta() {
  const res = await fetch("/api/meta");
  state.meta = await res.json();
  $("disclaimer").textContent = state.meta.disclaimer || "";
  $("privacyText").textContent = state.meta.privacy || "";
}

function setBusy(on, message) {
  $("busy").hidden = !on;
  $("analyzeBtn").disabled = on || (!state.file && !state.pastedText);
  if (message) $("status").textContent = message;
}

function openModal(id) {
  $(id).hidden = false;
}
function closeModal(id) {
  $(id).hidden = true;
}

function askPrivacy(next) {
  state.pending = next;
  $("privacyCheck").checked = false;
  openModal("privacyModal");
}

async function analyze(formData) {
  setBusy(true, "Analyzing your health document… this can take a moment.");
  try {
    const res = await fetch("/api/analyze", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(_error(data) || "Analysis failed.");
    applyResult(data);
  } catch (err) {
    $("status").textContent = err.message;
    alert(err.message);
  } finally {
    setBusy(false);
  }
}

function applyResult(data) {
  state.documentId = data.document_id;
  $("v-provider").textContent = data.overview.insurance_provider;
  $("v-member").textContent = data.overview.member_name;
  $("v-dates").textContent = data.overview.service_dates;
  $("v-claim").textContent = data.overview.claim_number;
  $("v-type").textContent = data.overview.document_type;
  const high = data.risk_counts.high || 0;
  const med = data.risk_counts.medium || 0;
  const low = data.risk_counts.low || 0;
  $("highCaption").textContent = `${high} item(s). Items that may need immediate attention.`;
  $("medCaption").textContent = `${med} item(s). Items to review or clarify.`;
  $("lowCaption").textContent = `${low} item(s). Standard information with minimal concern.`;
  if (data.findings && data.findings.length) {
    $("analysisIntro").textContent = data.findings
      .slice(0, 4)
      .map((item) => `${item.name} (${item.risk_level})`)
      .join("  ·  ");
  } else {
    $("analysisIntro").textContent = `Analysis complete for ${data.name}.`;
  }
  let explanation = data.plain_language || "No additional explanation was generated.";
  if (data.processing_notes && data.processing_notes.length) {
    explanation += `\n\nNotes: ${data.processing_notes.join(" ")}`;
  }
  $("plainLanguage").textContent = explanation;
  $("plainLanguage").style.color = "#4a2c1a";
  $("status").textContent = `Analysis complete for ${data.name}.`;
}

function setReady(label) {
  $("fileName").textContent = label;
  $("analyzeBtn").disabled = false;
  $("status").textContent = "Document ready. Click Analyze Document when you want to start.";
}

function queueFile(file) {
  state.file = file;
  state.pastedText = "";
  setReady(file.name);
}

function queueText(text) {
  state.file = null;
  state.pastedText = text;
  setReady("Pasted text");
}

function startAnalysis() {
  if (!state.file && !state.pastedText) {
    alert("Choose a file or paste text first.");
    return;
  }
  askPrivacy(() => {
    const form = new FormData();
    form.append("privacy_accepted", "true");
    if (state.file) form.append("file", state.file);
    else form.append("pasted_text", state.pastedText);
    analyze(form);
  });
}

async function draftLetter(kind) {
  if (!state.documentId) {
    alert("Upload or paste a document first.");
    return;
  }
  $("letterTitle").textContent = kind === "claim" ? "Create a Claim" : "Create an Appeal";
  $("letterStatus").textContent = "Drafting from your document…";
  $("letterText").value = "";
  openModal("letterModal");
  setBusy(true);
  try {
    const form = new FormData();
    form.append("document_id", state.documentId);
    form.append("kind", kind);
    const res = await fetch("/api/letter", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(_error(data) || "Could not draft the letter.");
    $("letterText").value = data.letter;
    $("letterStatus").textContent = "Review this draft against the original document before sending.";
  } catch (err) {
    $("letterStatus").textContent = err.message;
  } finally {
    setBusy(false);
  }
}

const dropZone = $("dropZone");
dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("drag");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag"));
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("drag");
  const file = event.dataTransfer.files[0];
  if (file) queueFile(file);
});

$("fileInput").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) queueFile(file);
  event.target.value = "";
});

$("analyzeBtn").addEventListener("click", startAnalysis);

$("pasteBtn").addEventListener("click", () => openModal("pasteModal"));
$("pasteSubmit").addEventListener("click", () => {
  const text = $("pasteArea").value.trim();
  if (!text) {
    alert("Paste some document text first.");
    return;
  }
  closeModal("pasteModal");
  queueText(text);
});

$("claimBtn").addEventListener("click", () => draftLetter("claim"));
$("appealBtn").addEventListener("click", () => draftLetter("appeal"));
$("copyLetter").addEventListener("click", async () => {
  await navigator.clipboard.writeText($("letterText").value);
  $("letterStatus").textContent = "Copied to the clipboard.";
});

$("privacyContinue").addEventListener("click", () => {
  if (!$("privacyCheck").checked) {
    alert("Please confirm you understand how document text is used.");
    return;
  }
  closeModal("privacyModal");
  const next = state.pending;
  state.pending = null;
  if (next) next();
});

document.querySelectorAll("[data-close]").forEach((button) => {
  button.addEventListener("click", () => closeModal(button.dataset.close));
});

loadMeta();
