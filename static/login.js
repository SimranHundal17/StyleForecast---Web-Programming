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

  // UI Configuration
  const UI_CONFIG = {
    login: {
      title: "Welcome Back",
      subtitle: "Log in to your Style Forecast account",
      button: "Login",
      footer: 'Don\'t have an account? <a href="#" class="switch-link">Sign Up</a>'
    },
    signup: {
      title: "Create Account",
      subtitle: "Sign up for your new Style Forecast account",
      button: "Sign Up",
      footer: 'Already have an account? <a href="#" class="switch-link">Login</a>'
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

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    // Validate inputs
    if (!validateInputs(email, password)) {
      return;
    }

    // Clear previous alerts
    hideAlert(successAlert);

    // Show loading state
    setLoading(true);

    // Handle signup or login
    if (isSignupMode) {
      await handleSignup(email, password);
    } else {
      await handleLogin(email, password);
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