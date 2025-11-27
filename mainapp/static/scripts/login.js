import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// 1. Initialize using the global window variable (defined in HTML)
const app = initializeApp(window.firebaseConfig);
const auth = getAuth(app);

// State
window.currentMode = "login";
window.resendTimer = null;

// Status helper
function setStatus(msg, type = "normal") {
  const el = document.getElementById("status");
  el.innerText = msg;
  el.style.color = type === "error" ? "#dc3545" : "#88a494";
}

// Security Reporter
async function reportFailure(identifier) {
  try {
    const res = await fetch("/api/report_failure/", {
      method: "POST",
      body: JSON.stringify({ identifier }),
    });
    const data = await res.json();
    if (data.status === "blocked") {
      setStatus(data.message, "error");
      document.querySelectorAll("button").forEach((b) => (b.disabled = true));
      return true;
    }
  } catch (e) {
    console.error(e);
  }
  return false;
}

// TIMER FUNCTION
window.startCooldown = () => {
  const btn = document.getElementById("resend-btn");
  let timeLeft = 60;

  btn.disabled = true;
  btn.innerText = `Resend Code (${timeLeft}s)`;

  if (window.resendTimer) clearInterval(window.resendTimer);

  window.resendTimer = setInterval(() => {
    timeLeft--;
    btn.innerText = `Resend Code (${timeLeft}s)`;

    if (timeLeft <= 0) {
      clearInterval(window.resendTimer);
      btn.disabled = false;
      btn.innerText = "Resend Code";
    }
  }, 1000);
};

// EMAIL LOGIN
window.handleEmailLogin = async () => {
  const email = document.getElementById("login-email").value;
  const pass = document.getElementById("login-password").value;

  if (!email || !pass) return setStatus("Please fill all fields", "error");
  setStatus("Authenticating...");

  try {
    const cred = await signInWithEmailAndPassword(auth, email, pass);
    completeBackendLogin(cred.user);
  } catch (error) {
    setStatus("Login failed. Check credentials.", "error");
    await reportFailure(email);
  }
};

// SEND EMAIL OTP
window.sendEmailOtp = async () => {
  const email = document.getElementById("reg-email").value;
  if (!email) return setStatus("Enter email first", "error");

  setStatus("Sending code...");

  // Disable buttons
  const resendBtn = document.getElementById("resend-btn");
  if (resendBtn) resendBtn.disabled = true;

  const res = await fetch("/api/send_email_otp/", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
  const data = await res.json();

  if (data.status === "success") {
    document.getElementById("email-reg-step1").classList.add("hidden");
    document.getElementById("email-reg-step2").classList.remove("hidden");
    setStatus("Code sent!");
    startCooldown();
  } else {
    setStatus(data.message, "error");
    if (resendBtn) resendBtn.disabled = false;
  }
};

// VERIFY EMAIL OTP (FIXED SECTION)
window.verifyEmailOtp = async () => {
  const otp = document.getElementById("reg-email-otp").value;
  // --- FIX START: We must get the email too! ---
  const email = document.getElementById("reg-email").value;
  // --- FIX END ---

  setStatus("Verifying...");

  const res = await fetch("/api/verify_email_otp/", {
    method: "POST",
    // We send BOTH email and otp now
    body: JSON.stringify({ email: email, otp: otp }),
  });
  const data = await res.json();

  if (data.status === "success") {
    document.getElementById("email-reg-step2").classList.add("hidden");
    document.getElementById("email-reg-step3").classList.remove("hidden");
    setStatus("Email verified.");
  } else {
    setStatus("Incorrect Code.", "error");
  }
};

// FINAL REGISTER
window.finalizeEmailRegister = async () => {
  const email = document.getElementById("reg-email").value;
  const pass = document.getElementById("reg-password").value;
  const confirm = document.getElementById("reg-confirm").value;

  if (pass !== confirm) return setStatus("Passwords do not match", "error");
  if (pass.length < 6) return setStatus("Password too short", "error");

  try {
    await createUserWithEmailAndPassword(auth, email, pass);
    await signOut(auth);

    setMode("login");
    document.getElementById("login-email").value = email;
    document.getElementById("reg-password").value = "";
    document.getElementById("reg-confirm").value = "";

    setStatus("Success! Please log in.", "normal");
  } catch (e) {
    setStatus(e.message, "error");
  }
};

async function completeBackendLogin(user) {
  setStatus("Securing session...");
  const token = await user.getIdToken();

  const res = await fetch("/api/login/", {
    method: "POST",
    body: JSON.stringify({ token }),
  });

  if (res.ok) {
    // Redirect to home page on success
    window.location.href = "/";
  } else {
    const d = await res.json();
    setStatus(d.message || "Login blocked.", "error");
  }
}

// MODE SWITCHING (Visual Update)
window.setMode = (mode) => {
  window.currentMode = mode;
  const title = document.getElementById("page-title");
  const subtitle = document.getElementById("page-subtitle");

  if (mode === "login") {
    document.getElementById("email-login-view").classList.remove("hidden");
    document.getElementById("email-register-view").classList.add("hidden");
    title.innerText = "Welcome Back";
    subtitle.innerText = "Login to your account";
  } else {
    document.getElementById("email-login-view").classList.add("hidden");
    document.getElementById("email-register-view").classList.remove("hidden");
    // Reset steps
    document.getElementById("email-reg-step1").classList.remove("hidden");
    document.getElementById("email-reg-step2").classList.add("hidden");
    document.getElementById("email-reg-step3").classList.add("hidden");
    title.innerText = "Register";
    subtitle.innerText = "Create your new account";
  }
  setStatus(""); // Clear errors
};
