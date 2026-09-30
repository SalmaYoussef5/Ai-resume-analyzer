const Api = (() => {
  const TOKEN_KEY = "docket_token";
  const USER_KEY = "docket_user";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function getUser() {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function requireAuth() {
    if (!getToken()) {
      window.location.href = "/index.html";
    }
  }

  async function request(path, { method = "GET", body = null, isForm = false, auth = true } = {}) {
    const headers = {};
    if (auth) {
      const token = getToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }
    if (body && !isForm) headers["Content-Type"] = "application/json";

    const res = await fetch(path, {
      method,
      headers,
      body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
    });

    if (res.status === 401 && auth) {
      clearSession();
      window.location.href = "/index.html";
      return null;
    }

    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }

    if (!res.ok) {
      const message = (data && data.detail) ? data.detail : `Request failed (${res.status})`;
      throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }

    return data;
  }

  return { getToken, setSession, getUser, clearSession, requireAuth, request };
})();

function showToast(message, isError = false) {
  let toast = document.getElementById("docket-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "docket-toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = "toast show" + (isError ? " error" : "");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function renderNav(activePage) {
  const el = document.getElementById("nav-root");
  if (!el) return;
  const user = Api.getUser();

  el.innerHTML = `
    <div class="topbar">
      <div class="topbar-inner">
        <a href="/jobs.html" class="wordmark">Docket<span class="dot">.</span></a>
        <div class="nav-links">
          <a href="/jobs.html" class="${activePage === 'jobs' ? 'active' : ''}">Open roles</a>
          <a href="/resumes.html" class="${activePage === 'resumes' ? 'active' : ''}">My résumés</a>
          <a href="/career.html" class="${activePage === 'career' ? 'active' : ''}">Advisor</a>
        </div>
        <div class="nav-right">
          <span class="nav-user">${user ? user.name : ""}</span>
          <button class="btn btn-ghost btn-small" onclick="logout()">Sign out</button>
        </div>
      </div>
    </div>
  `;
}

async function logout() {
  try {
    await Api.request("/auth/logout", { method: "POST" });
  } catch (e) {
  
  }
  Api.clearSession();
  window.location.href = "/index.html";
}
