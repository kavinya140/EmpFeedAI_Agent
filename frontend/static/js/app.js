const API = "/api";
const loginScreen = document.getElementById("login-screen");
const appRoot = document.getElementById("app-root");

function showApp() {
  loginScreen.classList.add("hidden");
  appRoot.classList.remove("hidden");
  updateWelcomeMessage();
}

function showLogin() {
  loginScreen.classList.remove("hidden");
  appRoot.classList.add("hidden");
}

function updateWelcomeMessage() {
  const welcome = document.getElementById("welcome-msg");
  const storedUser = localStorage.getItem("hr-suite-user");
  if (welcome) {
    if (storedUser) {
      const userName = storedUser.split("@")[0];
      welcome.textContent = `Welcome back, ${userName}! Ready to see the latest HR insights?`;
    } else {
      welcome.textContent =
        "Welcome back! Ready to see the latest HR sentiment and recommendations?";
    }
  }
}

const isLoggedIn = localStorage.getItem("hr-suite-auth") === "true";
if (isLoggedIn) {
  showApp();
} else {
  showLogin();
}

document.getElementById("login-form")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  if (!email || !password) return;
  localStorage.setItem("hr-suite-auth", "true");
  localStorage.setItem("hr-suite-user", email);
  showApp();
  showToast("Welcome back!");
});

document.getElementById("toggle-password")?.addEventListener("click", () => {
  const input = document.getElementById("login-password");
  const button = document.getElementById("toggle-password");
  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";
  button.textContent = isHidden ? "Hide" : "Show";
});

const logoutButton = document.createElement("button");
logoutButton.className = "nav-btn";
logoutButton.textContent = "🚪 Logout";
logoutButton.addEventListener("click", () => {
  localStorage.removeItem("hr-suite-auth");
  showLogin();
});

const nav = document.querySelector(".sidebar nav");
if (nav) {
  nav.appendChild(logoutButton);
}

function activateTab(tab) {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });

  const section = document.getElementById(`tab-${tab}`);
  if (section) {
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  if (tab === "dashboard") loadDashboard();
}

document.querySelectorAll(".nav-btn, .hero-actions .btn").forEach((btn) => {
  btn.addEventListener("click", (event) => {
    const targetTab = btn.dataset.tab || btn.dataset.tabTarget;
    if (targetTab) {
      event.preventDefault();
      activateTab(targetTab);
    }
  });
});

function setTheme(theme) {
  document.body.classList.toggle("light-theme", theme === "light");
  localStorage.setItem("feedback-theme", theme);
  const toggle = document.getElementById("theme-toggle");
  if (toggle) toggle.textContent = theme === "light" ? "☾" : "☀︎";
}

const savedTheme = localStorage.getItem("feedback-theme") || "dark";
setTheme(savedTheme);

document.getElementById("theme-toggle")?.addEventListener("click", () => {
  const next = document.body.classList.contains("light-theme")
    ? "dark"
    : "light";
  setTheme(next);
});

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  setTimeout(() => toast.classList.add("hidden"), 3500);
}

async function checkStatus() {
  const badge = document.getElementById("status-badge");
  try {
    const res = await fetch(`${API}/status`);
    const data = await res.json();
    badge.textContent = data.llm_configured
      ? "● Live • LLM ready"
      : "● Live • No LLM key";
    badge.className = "status-badge online";
    return data;
  } catch {
    badge.textContent = "● Offline";
    badge.className = "status-badge offline";
    return null;
  }
}

document.getElementById("is-anonymous")?.addEventListener("change", (e) => {
  document.getElementById("employee-name").disabled = e.target.checked;
});

document
  .getElementById("feedback-form")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "Analyzing...";

    const payload = {
      feedback_text: document.getElementById("feedback-text").value.trim(),
      department: document.getElementById("department").value,
      is_anonymous: document.getElementById("is-anonymous").checked,
      employee_name:
        document.getElementById("employee-name").value.trim() || null,
    };

    try {
      const res = await fetch(`${API}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Submission failed");

      showAnalysisResult(data.feedback);
      showToast("Feedback submitted and analyzed successfully!");
      document.getElementById("feedback-form").reset();
      document.getElementById("employee-name").disabled = true;
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Analyze & Submit";
    }
  });

function showAnalysisResult(fb) {
  const el = document.getElementById("analysis-result");
  el.classList.remove("hidden");
  el.innerHTML = `
    <h3>AI Analysis Result</h3>
    <div class="analysis-grid">
      <div class="analysis-item"><label>Sentiment</label><span class="badge">${fb.sentiment}</span></div>
      <div class="analysis-item"><label>Score</label><span>${(fb.sentiment_score * 100).toFixed(0)}%</span></div>
      <div class="analysis-item"><label>Category</label><span>${fb.category}</span></div>
      <div class="analysis-item"><label>Urgency</label><span class="badge">${fb.urgency}</span></div>
    </div>
    <p><strong>Summary:</strong> ${fb.summary}</p>
    <p><strong>Themes:</strong></p>
    <ul class="themes-list">${(fb.themes || []).map((t) => `<li>${t}</li>`).join("")}</ul>
    <p><strong>Recommended Actions:</strong></p>
    <ul class="actions-list">${(fb.action_items || []).map((a) => `<li>${a}</li>`).join("")}</ul>
    <p style="margin-top:0.75rem;font-size:0.8rem;color:var(--text-muted)">Analysis mode: ${fb.analysis_mode || "llm"}</p>
  `;
}

async function loadDashboard() {
  try {
    const [analyticsRes, feedbackRes] = await Promise.all([
      fetch(`${API}/analytics`),
      fetch(`${API}/feedback?limit=20`),
    ]);
    const analytics = await analyticsRes.json();
    const feedbackData = await feedbackRes.json();

    animateValue("stat-total", analytics.total_feedback ?? 0);
    animateValue(
      "stat-sentiment",
      analytics.avg_sentiment_score != null
        ? `${(analytics.avg_sentiment_score * 100).toFixed(0)}%`
        : "—",
      true,
    );
    animateValue("stat-index", analytics.vector_index_count ?? 0);
    animateValue(
      "stat-llm",
      analytics.llm_configured ? "Ready" : "No Key",
      true,
    );

    renderFeedbackList(feedbackData.feedback || []);
  } catch (err) {
    showToast("Failed to load dashboard", "error");
  }
}

function animateValue(id, value, isText = false) {
  const el = document.getElementById(id);
  if (!el) return;
  if (isText) {
    el.textContent = value;
    return;
  }
  const start = 0;
  const end = Number(value || 0);
  const duration = 800;
  let startTime = null;
  const step = (timestamp) => {
    if (!startTime) startTime = timestamp;
    const progress = Math.min((timestamp - startTime) / duration, 1);
    el.textContent = Math.floor(progress * end);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function renderFeedbackList(items) {
  const container = document.getElementById("feedback-list");
  if (!container) return;
  if (!items.length) {
    container.innerHTML =
      '<div class="empty-state">No feedback submitted yet.</div>';
    return;
  }
  container.innerHTML = items
    .map(
      (fb) => `
    <div class="feedback-item">
      <div class="feedback-meta">
        <span class="badge">${fb.sentiment}</span>
        <span class="badge">${fb.department}</span>
        ${fb.urgency === "high" ? '<span class="badge badge-urgency-high">urgent</span>' : ""}
      </div>
      <div class="feedback-text">${escapeHtml(fb.feedback_text?.substring(0, 200))}${fb.feedback_text?.length > 200 ? "..." : ""}</div>
      <div class="feedback-summary">${escapeHtml(fb.summary || "")}</div>
    </div>
  `,
    )
    .join("");
}

document.getElementById("search-btn")?.addEventListener("click", async () => {
  const q = document.getElementById("search-query").value.trim();
  if (q.length < 3) return showToast("Enter at least 3 characters", "error");

  try {
    const res = await fetch(
      `${API}/feedback/search?q=${encodeURIComponent(q)}`,
    );
    const data = await res.json();
    const container = document.getElementById("search-results");
    if (!data.results?.length) {
      container.innerHTML =
        '<div class="empty-state">No matching feedback found.</div>';
      return;
    }
    container.innerHTML = data.results
      .map(
        (fb) => `
      <div class="feedback-item">
        <div class="feedback-meta">
          <span class="badge">${fb.sentiment || "N/A"}</span>
          <span class="badge">${fb.department || "N/A"}</span>
        </div>
        <div class="feedback-text">${escapeHtml(fb.feedback_text?.substring(0, 200) || fb.summary || "")}</div>
      </div>
    `,
      )
      .join("");
  } catch {
    showToast("Search failed", "error");
  }
});

document.getElementById("chat-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-question");
  const question = input.value.trim();
  if (!question) return;

  appendChatMsg(question, "user");
  input.value = "";

  const container = document.getElementById("chat-messages");
  const loading = document.createElement("div");
  loading.className = "chat-msg agent";
  loading.textContent = "Thinking...";
  container.appendChild(loading);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    loading.remove();
    if (!res.ok) throw new Error(data.detail || "Chat failed");
    appendChatMsg(data.answer, "agent");
  } catch (err) {
    loading.remove();
    appendChatMsg(`Error: ${err.message}`, "agent");
  }
});

function appendChatMsg(text, role) {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  if (role === "agent") {
    // Render agent replies as bullet-point lists for readability.
    const escaped = escapeHtml(text || "");
    // Split by blank lines or single newlines; if single chunk, split into sentences.
    let parts = escaped.split(/\n\s*\n/).flatMap((p) => p.split(/\n/));
    if (parts.length === 1) {
      parts = escaped.match(/[^\.\!\?]+[\.\!\?]*/g) || [escaped];
    }
    const ul = document.createElement("ul");
    ul.className = "agent-bullets";
    parts.forEach((pt) => {
      const s = pt.trim();
      if (!s) return;
      const li = document.createElement("li");
      li.innerHTML = s;
      ul.appendChild(li);
    });
    div.appendChild(ul);
  } else {
    div.textContent = text;
  }
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

let generatedReportText = "";

const downloadReportBtn = document.getElementById("download-report-btn");

document
  .getElementById("generate-report-btn")
  ?.addEventListener("click", async () => {
    const btn = document.getElementById("generate-report-btn");
    const output = document.getElementById("report-output");
    btn.disabled = true;
    btn.textContent = "Generating...";
    downloadReportBtn?.classList.add("hidden");
    output.classList.remove("hidden");
    output.textContent = "Generating executive report...";

    try {
      const res = await fetch(`${API}/report`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Report failed");
      generatedReportText = data.report;
      output.innerHTML = formatReport(generatedReportText);
      if (downloadReportBtn) {
        downloadReportBtn.classList.remove("hidden");
      }
    } catch (err) {
      output.textContent = `Error: ${err.message}`;
      generatedReportText = "";
    } finally {
      btn.disabled = false;
      btn.textContent = "Generate Report";
    }
  });

if (downloadReportBtn) {
  downloadReportBtn.addEventListener("click", () => {
    if (!generatedReportText) return;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const lines = doc.splitTextToSize(generatedReportText, 520);
    doc.setFontSize(12);
    doc.text(lines, 40, 60);
    doc.save("hr-report.pdf");
  });
}

function formatReport(text) {
  return text
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h2>$1</h2>")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

checkStatus();
loadDashboard();
