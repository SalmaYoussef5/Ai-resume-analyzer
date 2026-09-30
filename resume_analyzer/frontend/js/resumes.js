Api.requireAuth();
renderNav("resumes");

let resumes = [];
let selectedResumeId = null;

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

async function loadResumes(selectAfter = null) {
  const listEl = document.getElementById("resume-list");
  try {
    resumes = await Api.request("/resumes/");

    if (!resumes.length) {
      listEl.innerHTML = `<div class="placeholder-note" style="padding: 12px 0;">No résumés uploaded yet.</div>`;
      return;
    }

    listEl.innerHTML = resumes
      .map(
        (r) => `
        <div class="resume-item ${r.id === selectedResumeId ? "active" : ""}" onclick="selectResume(${r.id})">
          <span class="fname">${escapeHtml(r.file_name)}</span>
        </div>
      `
      )
      .join("");

    const toSelect = selectAfter ?? (resumes.find((r) => r.id === selectedResumeId) ? selectedResumeId : resumes[0].id);
    selectResume(toSelect);
  } catch (err) {
    listEl.innerHTML = `<div class="placeholder-note">Could not load résumés.</div>`;
  }
}

function selectResume(id) {
  selectedResumeId = id;
  document.querySelectorAll(".resume-item").forEach((el, i) => {
    el.classList.toggle("active", resumes[i] && resumes[i].id === id);
  });
  renderResumeDetail();
}

function renderResumeDetail() {
  const resume = resumes.find((r) => r.id === selectedResumeId);
  const detail = document.getElementById("resume-detail");
  if (!resume) {
    detail.innerHTML = `<div class="placeholder-note">Select a résumé on the left, or upload a new one to begin.</div>`;
    return;
  }

  detail.innerHTML = `
    <div class="page-head" style="border-bottom:none; margin-bottom:18px;">
      <div>
        <h2>${escapeHtml(resume.file_name)}</h2>
      </div>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-brass btn-small" onclick="runMatch(${resume.id})">Find matching roles</button>
        <button class="btn btn-danger-ghost btn-small" onclick="deleteResume(${resume.id})">Delete</button>
      </div>
    </div>

    <p>${escapeHtml(resume.summary || "No summary available.")}</p>

    <hr class="hr" />

    <dl class="kv-grid">
      <dt>Technical skills</dt>
      <dd><div class="chip-group">${(resume.technical_skills || []).map((s) => `<span class="chip">${escapeHtml(s)}</span>`).join("") || "—"}</div></dd>

      <dt>Soft skills</dt>
      <dd><div class="chip-group">${(resume.soft_skills || []).map((s) => `<span class="chip">${escapeHtml(s)}</span>`).join("") || "—"}</div></dd>

      <dt>Education</dt>
      <dd>${(resume.education || []).map((e) => escapeHtml(e)).join("<br/>") || "—"}</dd>

      <dt>Experience</dt>
      <dd>${(resume.experience || []).map((e) => escapeHtml(e)).join("<br/>") || "—"}</dd>
    </dl>

    <hr class="hr" />

    <div class="section-label">Matching roles</div>
    <div id="matches-area">
      <div class="placeholder-note" style="padding: 20px 0;">Run matching to see ranked roles here.</div>
    </div>
  `;

  loadSavedMatches(resume.id);
}

async function loadSavedMatches(resumeId) {
  const area = document.getElementById("matches-area");
  try {
    const matches = await Api.request(`/resumes/${resumeId}/matches`);
    renderMatches(matches);
  } catch (err) {
    
  }
}

function renderMatches(matches) {
  const area = document.getElementById("matches-area");
  if (!matches.length) {
    area.innerHTML = `<div class="placeholder-note" style="padding: 20px 0;">No matches yet.</div>`;
    return;
  }
  area.innerHTML = matches
    .map(
      (m) => `
      <div class="match-row">
        <div class="match-score">${m.match_score}<span class="unit">%</span></div>
        <div class="match-body">
          <div class="match-title">${escapeHtml(m.job_title)}</div>
          <div class="match-explain">${escapeHtml(m.explanation)}</div>
        </div>
      </div>
    `
    )
    .join("");
}

async function runMatch(resumeId) {
  const area = document.getElementById("matches-area");
  area.innerHTML = `<div class="spinner-text" style="padding: 20px 0;">Comparing against open roles — this can take a few seconds…</div>`;
  try {
    const matches = await Api.request(`/resumes/${resumeId}/match`, { method: "POST" });
    renderMatches(matches);
  } catch (err) {
    area.innerHTML = `<div class="placeholder-note">${escapeHtml(err.message)}</div>`;
  }
}

async function deleteResume(resumeId) {
  if (!confirm("Delete this résumé permanently?")) return;
  try {
    await Api.request(`/resumes/${resumeId}`, { method: "DELETE" });
    showToast("Résumé deleted.");
    selectedResumeId = null;
    loadResumes();
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("file-input").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  showToast("Uploading and analyzing résumé…");
  try {
    const resume = await Api.request("/resumes/upload", { method: "POST", body: formData, isForm: true });
    showToast("Résumé analyzed.");
    e.target.value = "";
    loadResumes(resume.id);
  } catch (err) {
    showToast(err.message, true);
    e.target.value = "";
  }
});

loadResumes();
