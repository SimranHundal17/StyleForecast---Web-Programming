document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const title = document.querySelector(".auth-title");
  const subtitle = document.querySelector(".auth-subtitle");
  const button = document.getElementById("submitBtn");
  const footer = document.querySelector(".auth-footer");
  const successAlert = document.getElementById("loginSuccess");
  const loadingSpinner = document.getElementById("loginLoading");

  let isSignupMode = false;

  // Toggle Login/Signup
  window.toggleForm = function (event) {
    event.preventDefault();
    isSignupMode = !isSignupMode;

    if (isSignupMode) {
      title.textContent = "Create Account";
      subtitle.textContent = "Sign up for your new Style Forecast account";
      button.textContent = "Sign Up";
      footer.innerHTML =
        'Already have an account? <a href="#" class="switch-link" onclick="toggleForm(event)">Login</a>';
    } else {
      title.textContent = "Welcome Back";
      subtitle.textContent = "Log in to your Style Forecast account";
      button.textContent = "Login";
      footer.innerHTML =
        'Don’t have an account? <a href="#" class="switch-link" onclick="toggleForm(event)">Sign Up</a>';
    }
  };

  // Handle Login / Signup submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      alert("Please fill in all fields.");
      return;
    }

    loadingSpinner.classList.remove("d-none");

    try {
      if (isSignupMode) {
        // 🔹 Fake signup (frontend only)
        await new Promise((r) => setTimeout(r, 1000));
        loadingSpinner.classList.add("d-none");
        successAlert.textContent = "🎉 Account Created! You can now log in.";
        successAlert.classList.remove("d-none");

        setTimeout(() => {
          toggleForm(new Event("click"));
          successAlert.classList.add("d-none");
        }, 2000);
      } else {
        // 🔹 Real login request
        const response = await fetch("/login", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ email, password }),
        });

        const data = await response.json();
        loadingSpinner.classList.add("d-none");

        if (data.success) {
          successAlert.textContent = "✅ Login Successful! Redirecting...";
          successAlert.classList.remove("d-none");
          setTimeout(() => {
            window.location.href = data.redirect_url;
          }, 1500);
        } else {
          alert(data.message || "Invalid credentials");
        }
      }
    } catch (err) {
      console.error("Error:", err);
      loadingSpinner.classList.add("d-none");
      alert("Something went wrong. Please try again.");
    }
  });
});
