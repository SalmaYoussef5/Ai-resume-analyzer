Api.requireAuth();
renderNav("career");

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

async function populateSelectors() {
  try {
    const resumes = await Api.request("/resumes/");
    const options = resumes.map((r) => `<option value="${r.id}">${escapeHtml(r.file_name)}</option>`).join("");
    document.getElementById("q-resume").insertAdjacentHTML("beforeend", options);
    document.getElementById("i-resume").innerHTML = options || `<option value="">No résumés uploaded yet</option>`;
  } catch (err) {
   
  }

  try {
    const jobs = await Api.request("/jobs/");
    const options = jobs.map((j) => `<option value="${j.id}">${escapeHtml(j.title)}</option>`).join("");
    document.getElementById("i-job").insertAdjacentHTML("beforeend", options);
  } catch (err) {
    
  }
}

async function askQuestion() {
  const question = document.getElementById("q-input").value.trim();
  if (!question) {
    showToast("Type a question first.", true);
    return;
  }
  const resumeId = document.getElementById("q-resume").value;

  const thread = document.getElementById("qa-thread");
  const pendingId = `qa-${Date.now()}`;
  thread.insertAdjacentHTML(
    "afterbegin",
    `<div class="qa-item" id="${pendingId}">
      <div class="qa-question">${escapeHtml(question)}</div>
      <div class="qa-answer spinner-text">Thinking…</div>
    </div>`
  );
  document.getElementById("q-input").value = "";

  try {
    const payload = { question };
    if (resumeId) payload.resume_id = Number(resumeId);
    const res = await Api.request("/career/ask", { method: "POST", body: payload });
    document.querySelector(`#${pendingId} .qa-answer`).textContent = res.answer;
    document.querySelector(`#${pendingId} .qa-answer`).classList.remove("spinner-text");
  } catch (err) {
    document.querySelector(`#${pendingId} .qa-answer`).textContent = "Could not get an answer: " + err.message;
  }
}

async function requestImprovement() {
  const resumeId = document.getElementById("i-resume").value;
  const jobId = document.getElementById("i-job").value;
  const area = document.getElementById("improvement-area");

  if (!resumeId) {
    showToast("Upload a résumé first from My résumés.", true);
    return;
  }

  area.innerHTML = `<div class="spinner-text" style="padding: 16px 0;">Comparing against the knowledge base…</div>`;

  try {
    const url = `/career/resumes/${resumeId}/improve` + (jobId ? `?job_id=${jobId}` : "");
    const res = await Api.request(url, { method: "POST" });

    area.innerHTML = `
      ${res.missing_skills.length ? `
        <div class="section-label" style="margin-top:20px;">Missing for this role</div>
        <div class="chip-group">${res.missing_skills.map((s) => `<span class="chip chip-missing">${escapeHtml(s)}</span>`).join("")}</div>
      ` : ""}
      <div class="advice-block">${escapeHtml(res.advice)}</div>
    `;
  } catch (err) {
    area.innerHTML = `<div class="placeholder-note">${escapeHtml(err.message)}</div>`;
  }
}

populateSelectors();
