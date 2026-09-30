Api.requireAuth();
renderNav("jobs");

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function openPostForm() {
  document.getElementById("post-form-wrap").style.display = "block";
}
function closePostForm() {
  document.getElementById("post-form-wrap").style.display = "none";
}

function clearFilters() {
  ["f-title", "f-location", "f-category", "f-skill"].forEach((id) => (document.getElementById(id).value = ""));
  loadJobs();
}

function buildQuery() {
  const params = new URLSearchParams();
  const map = { "f-title": "title", "f-location": "location", "f-category": "category", "f-skill": "skill" };
  for (const [id, key] of Object.entries(map)) {
    const val = document.getElementById(id).value.trim();
    if (val) params.set(key, val);
  }
  const qs = params.toString();
  return qs ? `/jobs/?${qs}` : "/jobs/";
}

async function loadJobs() {
  const listEl = document.getElementById("jobs-list");
  listEl.innerHTML = `<div class="placeholder-note">Loading roles…</div>`;

  try {
    const jobs = await Api.request(buildQuery());

    if (!jobs.length) {
      listEl.innerHTML = `<div class="empty-state">No roles match these filters yet.</div>`;
      return;
    }

    const user = Api.getUser();

    listEl.innerHTML = jobs
      .map((job, i) => {
        const num = String(i + 1).padStart(2, "0");
        const skills = job.required_skills.split(",").map((s) => s.trim()).filter(Boolean);
        const isMine = user && job.posted_by_id === user.id;

        return `
          <div class="entry-row">
            <div class="entry-index">${num}</div>
            <div class="entry-body">
              <div class="entry-title-row">
                <h3 class="entry-title">${escapeHtml(job.title)}</h3>
                <div class="entry-meta">
                  ${job.location ? `<span>${escapeHtml(job.location)}</span>` : ""}
                  ${job.category ? `<span>${escapeHtml(job.category)}</span>` : ""}
                </div>
              </div>
              <p class="entry-desc">${escapeHtml(job.description)}</p>
              <div class="tag-row">
                ${skills.map((s) => `<span class="tag">${escapeHtml(s)}</span>`).join("")}
              </div>
              ${isMine ? `
                <div class="entry-actions">
                  <button class="btn btn-outline btn-small" onclick="deleteJob(${job.id})">Remove listing</button>
                </div>
              ` : ""}
            </div>
          </div>
        `;
      })
      .join("");
  } catch (err) {
    listEl.innerHTML = `<div class="empty-state">Could not load roles: ${escapeHtml(err.message)}</div>`;
  }
}

async function submitJob() {
  const title = document.getElementById("p-title").value.trim();
  const location = document.getElementById("p-location").value.trim();
  const category = document.getElementById("p-category").value.trim();
  const required_skills = document.getElementById("p-skills").value.trim();
  const description = document.getElementById("p-desc").value.trim();

  if (!title || !required_skills || !description) {
    showToast("Please fill in the title, skills, and description.", true);
    return;
  }

  try {
    await Api.request("/jobs/", {
      method: "POST",
      body: { title, location, category, required_skills, description },
    });
    showToast("Role published.");
    closePostForm();
    ["p-title", "p-location", "p-category", "p-skills", "p-desc"].forEach((id) => (document.getElementById(id).value = ""));
    loadJobs();
  } catch (err) {
    showToast(err.message, true);
  }
}

async function deleteJob(jobId) {
  if (!confirm("Remove this listing? This can't be undone.")) return;
  try {
    await Api.request(`/jobs/${jobId}`, { method: "DELETE" });
    showToast("Listing removed.");
    loadJobs();
  } catch (err) {
    showToast(err.message, true);
  }
}

loadJobs();
