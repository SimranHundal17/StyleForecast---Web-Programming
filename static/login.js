// static/login.js

document.addEventListener("DOMContentLoaded", () => {
  // DOM elements
  const form = document.getElementById("loginForm");
  const title = document.querySelector(".auth-title");
  const subtitle = document.querySelector(".auth-subtitle");
  const submitBtn = document.getElementById("submitBtn");
  const footer = document.querySelector(".auth-footer");
  const successAlert = document.getElementById("loginSuccess");
  const loadingSpinner = document.getElementById("loginLoading");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");

  // State
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

  // Toggle between Login and Signup modes
  function toggleForm(event) {
    if (event) event.preventDefault();
    
    isSignupMode = !isSignupMode;
    const config = isSignupMode ? UI_CONFIG.signup : UI_CONFIG.login;

    // Update UI
    title.textContent = config.title;
    subtitle.textContent = config.subtitle;
    submitBtn.textContent = config.button;
    footer.innerHTML = config.footer;

    // Clear form and alerts
    form.reset();
    hideAlert(successAlert);
    
    // Re-attach event listeners to new footer link
    attachToggleListener();
  }

  // Attach click event to toggle link
  function attachToggleListener() {
    const switchLink = footer.querySelector(".switch-link");
    if (switchLink) {
      switchLink.addEventListener("click", toggleForm);
    }
  }

  // Show alert message
  function showAlert(element, message, type = "success") {
    element.textContent = message;
    element.className = `alert alert-${type}`;
    element.classList.remove("d-none");
  }

  // Hide alert message
  function hideAlert(element) {
    element.classList.add("d-none");
  }

  // Show/hide loading state
  function setLoading(isLoading) {
    if (isLoading) {
      loadingSpinner.classList.remove("d-none");
      submitBtn.disabled = true;
      submitBtn.textContent = isSignupMode ? "Creating Account..." : "Logging In...";
    } else {
      loadingSpinner.classList.add("d-none");
      submitBtn.disabled = false;
      submitBtn.textContent = isSignupMode ? "Sign Up" : "Login";
    }
  }

  // Validate form inputs
  function validateInputs(email, password) {
    if (!email || !password) {
      showAlert(successAlert, "⚠️ Please fill in all fields.", "warning");
      return false;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showAlert(successAlert, "⚠️ Please enter a valid email address.", "warning");
      return false;
    }

    // Password length validation
    if (password.length < 6) {
      showAlert(successAlert, "⚠️ Password must be at least 6 characters.", "warning");
      return false;
    }

    return true;
  }

  // Make API request
  async function makeAuthRequest(endpoint, email, password) {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ email, password }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // Handle signup
  async function handleSignup(email, password) {
    try {
      const data = await makeAuthRequest("/auth/register", email, password);

      if (data.success) {
        showAlert(successAlert, data.message || "🎉 Account created successfully!", "success");
        
        // Switch to login mode after delay
        setTimeout(() => {
          toggleForm();
          hideAlert(successAlert);
        }, 2000);
      } else {
        showAlert(successAlert, data.message || "❌ Registration failed. Please try again.", "danger");
      }
    } catch (error) {
      console.error("Signup error:", error);
      showAlert(successAlert, "❌ Network error. Please check your connection.", "danger");
    }
  }

  // Handle login
  async function handleLogin(email, password) {
    try {
      const endpoint = form.getAttribute("action") || "/auth/login";
      const data = await makeAuthRequest(endpoint, email, password);

      if (data.success) {
        showAlert(successAlert, "✅ Login successful! Redirecting...", "success");
        
        // Redirect after delay
        setTimeout(() => {
          window.location.href = data.redirect_url || "/wardrobe";
        }, 1500);
      } else {
        showAlert(successAlert, data.message || "❌ Invalid email or password.", "danger");
      }
    } catch (error) {
      console.error("Login error:", error);
      showAlert(successAlert, "❌ Network error. Please check your connection.", "danger");
    }
  }

  // Handle form submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      alert("Please fill in all required fields.");
      return;
    }

    // Clear previous alerts
    hideAlert(successAlert);

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

        const response = await fetch("/auth/signup", {
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
      const response = await fetch("/auth/login", {
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

    // Hide loading state
    setLoading(false);
  });

  // Initialize toggle listener
  attachToggleListener();

  // Auto-focus email input
  if (emailInput) {
    emailInput.focus();
  }
});