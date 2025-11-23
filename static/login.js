document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const title = document.querySelector(".auth-title");
  const subtitle = document.querySelector(".auth-subtitle");
  const button = document.getElementById("submitBtn");
  const footer = document.querySelector(".auth-footer");
  const successAlert = document.getElementById("loginSuccess");
  const loadingSpinner = document.getElementById("loginLoading");

  let isSignupMode = false;

  // Toggle Login/Signup mode
  window.toggleForm = function (event) {
    event.preventDefault();
    isSignupMode = !isSignupMode;

    const signupFields = document.getElementById("signupFields");
    const signupPassword = document.getElementById("signupPasswordFields");
    const signupExtra = document.getElementById("signupExtraFields");

    if (isSignupMode) {
      signupFields.classList.remove("d-none");
      signupPassword.classList.remove("d-none");
      signupExtra.classList.remove("d-none");

      title.textContent = "Create Account";
      subtitle.textContent = "Sign up for your new Style Forecast account";
      button.textContent = "Sign Up";

      footer.innerHTML =
        'Already have an account? <a href="#" class="switch-link" onclick="toggleForm(event)">Login</a>';

    } else {
      signupFields.classList.add("d-none");
      signupPassword.classList.add("d-none");
      signupExtra.classList.add("d-none");

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
      alert("Please fill in all required fields.");
      return;
    }

    loadingSpinner.classList.remove("d-none");

    try {
      // ------------------------------------------
      // SIGNUP MODE
      // ------------------------------------------
      if (isSignupMode) {
        const firstName = document.getElementById("first_name").value.trim();
        const lastName = document.getElementById("last_name").value.trim();
        const confirm = document.getElementById("confirm_password").value.trim();
        const gender = document.getElementById("gender").value;
        const age = document.getElementById("age").value;
        const daysDirty = document.getElementById("days_until_dirty").value;

        const signupData = {
          email,
          password,
          confirm_password: confirm,
          first_name: firstName,
          last_name: lastName,
          gender,
          age,
          days_until_dirty: daysDirty
        };

        const response = await fetch("/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(signupData)
        });

        const data = await response.json();
        loadingSpinner.classList.add("d-none");

        if (data.success) {
          successAlert.textContent = "🎉 Account Created! You can now log in.";
          successAlert.classList.remove("d-none");

          setTimeout(() => {
            toggleForm(new Event("click"));
            successAlert.classList.add("d-none");
          }, 2000);
        } else {
          alert(data.message);
        }

        return; // IMPORTANT: prevent running login block
      }

      // ------------------------------------------
      // LOGIN MODE
      // ------------------------------------------
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

    } catch (err) {
      console.error("Error:", err);
      loadingSpinner.classList.add("d-none");
      alert("Something went wrong. Please try again.");
    }
  });
});
