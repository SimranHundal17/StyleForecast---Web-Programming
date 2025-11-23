// Wait until the page is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Find the "Get Started" button
  const btn = document.querySelector(".get-started-btn");

  if (!btn) return;

  // On click, redirect to the login page
  btn.addEventListener("click", (event) => {
    event.preventDefault(); // prevent default link behavior

    // Use the same URL that is in the href attribute
    const targetUrl = btn.getAttribute("href");
    window.location.href = targetUrl;
  });
});
