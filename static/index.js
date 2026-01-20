/* ============================================================
   static/index.js — Intro page button behavior
   ============================================================
   Purpose:
   - Handle the "Get Started" button on the intro (landing) page.
   - Redirect the user to the login page when the button is clicked.

   What this file does:
   - Waits until the HTML page is fully loaded.
   - Finds the "Get Started" button by its CSS class.
   - Listens for a click on the button.
   - Prevents the default link behavior.
   - Redirects the user using JavaScript.

   Key ideas:
   - DOMContentLoaded ensures the DOM is ready before accessing elements.
   - event.preventDefault() stops the browser default action.
   - window.location.href is used for manual navigation.
============================================================ */

// Wait until the page is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Find the "Get Started" button on the page
  const btn = document.querySelector(".get-started-btn");

  // If button is not found, stop the script
  if (!btn) return;

  // Add click event to the button
  btn.addEventListener("click", (event) => {
    event.preventDefault(); // stop the default link behavior

    // Read the URL from the href attribute
    const targetUrl = btn.getAttribute("href");
    // Redirect the user to the login page
    window.location.href = targetUrl;
  });
});
