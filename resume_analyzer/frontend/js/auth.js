function switchTab(tab) {
  document.querySelectorAll(".auth-tab").forEach((el) => el.classList.toggle("active", el.dataset.tab === tab));
  document.querySelectorAll(".auth-form").forEach((el) => el.classList.toggle("active", el.dataset.tab === tab));
  document.getElementById("auth-error").style.display = "none";
}

function showAuthError(message) {
  const el = document.getElementById("auth-error");
  el.textContent = message;
  el.style.display = "block";
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  try {
    const tokenRes = await Api.request("/auth/login", { method: "POST", body: form, isForm: true, auth: false });
    Api.setSession(tokenRes.access_token, { email });

    const me = await Api.request("/auth/me");
    Api.setSession(tokenRes.access_token, me);

    window.location.href = "/jobs.html";
  } catch (err) {
    showAuthError(err.message || "Could not sign in.");
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;

  try {
    await Api.request("/auth/register", { method: "POST", body: { name, email, password }, auth: false });

    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const tokenRes = await Api.request("/auth/login", { method: "POST", body: form, isForm: true, auth: false });
    Api.setSession(tokenRes.access_token, { name, email });

    const me = await Api.request("/auth/me");
    Api.setSession(tokenRes.access_token, me);

    window.location.href = "/jobs.html";
  } catch (err) {
    showAuthError(err.message || "Could not create the account.");
  }
});

if (Api.getToken()) {
  window.location.href = "/jobs.html";
}
