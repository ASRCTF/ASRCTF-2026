const ADMIN_API_BASE = window.ASRCTF_ADMIN_API_BASE || "";
const PUBLIC_FILTER = window.ASRCTF_PUBLIC_FILTER || { enabled: false, blocked_phrases: [] };
const FILTER_TRANSLATION = {
  "@": "a",
  "4": "a",
  "3": "e",
  "1": "i",
  "!": "i",
  "|": "i",
  "0": "o",
  "$": "s",
  "5": "s",
  "7": "t",
  "+": "t",
};

async function fetchJson(url, options) {
  const response = await fetch(url, options || {});
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json();
}

function renderStatus(status) {
  const panel = document.getElementById("status-panel");
  if (!panel || !status) {
    return;
  }

  panel.querySelector('[data-field="backend"]').textContent = status.active_backend.mode;
  panel.querySelector('[data-field="version"]').textContent = status.active_backend.version;
  panel.querySelector('[data-field="requests"]').textContent = `${status.total_requests} total / ${status.active_requests} live`;

  panel.querySelector('[data-field="payloads"]').textContent = String(status.successful_payloads);
}

function renderEntries(containerId, entries, renderer) {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }

  if (!entries || !entries.length) {
    container.innerHTML = '<div class="entry"><p>No data yet.</p></div>';
    return;
  }

  container.innerHTML = entries.map(renderer).join("");
}

function renderEvents(entries) {
  renderEntries(
    "event-list",
    entries,
    (entry) => `
      <article class="entry">
        <p><strong>${entry.level.toUpperCase()}</strong> ${entry.message}</p>
        <small>${entry.timestamp}</small>
      </article>
    `
  );
}

function renderPayloads(entries) {
  renderEntries(
    "payload-list",
    entries,
    (entry) => `
      <article class="entry">
        <p><strong>Prompt:</strong> ${entry.prompt}</p>
        <p><strong>Response:</strong> ${entry.response}</p>
        <small>${entry.timestamp} | ${entry.backend_version}</small>
      </article>
    `
  );
}

async function refreshDashboard() {
  const panel = document.getElementById("status-panel");
  if (!panel || !ADMIN_API_BASE) {
    return;
  }

  try {
    const status = await fetchJson(`${ADMIN_API_BASE}/status`);
    renderStatus(status);
  } catch (error) {
    console.error(error);
  }
}

async function refreshEvents() {
  const container = document.getElementById("event-list");
  if (!container || !ADMIN_API_BASE) {
    return;
  }

  try {
    const payload = await fetchJson(`${ADMIN_API_BASE}/events`);
    renderEvents(payload.events);
  } catch (error) {
    console.error(error);
  }
}

async function refreshPayloads() {
  const container = document.getElementById("payload-list");
  if (!container || !ADMIN_API_BASE) {
    return;
  }

  try {
    const payload = await fetchJson(`${ADMIN_API_BASE}/payloads`);
    renderPayloads(payload.payloads);
  } catch (error) {
    console.error(error);
  }
}

async function postJson(url, body) {
  return fetchJson(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body || {}),
  });
}

function normalizeFilterText(text) {
  const translated = String(text || "")
    .toLowerCase()
    .split("")
    .map((char) => FILTER_TRANSLATION[char] || char)
    .join("");
  const normalized = translated.replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
  return {
    normalized,
    compact: normalized.replace(/\s+/g, ""),
  };
}

async function sendPrompt(event) {
  event.preventDefault();
  const textarea = document.getElementById("prompt-input");
  const output = document.getElementById("chat-response");
  const meta = document.getElementById("chat-meta");
  if (!textarea || !output || !meta) {
    return;
  }

  const prompt = textarea.value || "";
  const promptForms = normalizeFilterText(prompt);
  const blockedPhrase = (PUBLIC_FILTER.blocked_phrases || []).find((phrase) => {
    const phraseForms = normalizeFilterText(phrase);
    return (
      (phraseForms.normalized && promptForms.normalized.includes(phraseForms.normalized)) ||
      (phraseForms.compact && promptForms.compact.includes(phraseForms.compact))
    );
  });
  if (PUBLIC_FILTER.enabled && blockedPhrase) {
    output.textContent = PUBLIC_FILTER.message || "Basic prompt-injection phrases are filtered here. Use a more creative angle.";
    meta.innerHTML = '<span class="badge warning">filtered</span>';
    return;
  }

  output.textContent = "Sending prompt...";
  meta.innerHTML = "";

  try {
    const payload = await postJson("/api/chat", { prompt });
    output.textContent = payload.response;
    meta.innerHTML = `
      <span class="badge success">${payload.status === "ok" ? "response received" : payload.status}</span>
    `;
    refreshDashboard();
    refreshPayloads();
    refreshEvents();
  } catch (error) {
    output.textContent = String(error);
  }
}



function attachHandlers() {
  const chatForm = document.getElementById("chat-form");
  if (chatForm) {
    chatForm.addEventListener("submit", sendPrompt);
  }

  document.querySelectorAll("[data-action='refresh-status']").forEach((button) => {
    button.addEventListener("click", refreshDashboard);
  });
  document.querySelectorAll("[data-action='refresh-events']").forEach((button) => {
    button.addEventListener("click", refreshEvents);
  });

}

function boot() {
  attachHandlers();
  refreshDashboard();
  refreshEvents();
  refreshPayloads();
  window.setInterval(refreshDashboard, 4000);
}

window.addEventListener("DOMContentLoaded", boot);
