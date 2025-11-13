async function loadProfile() {
  const res = await fetch("/profile/data");
  const user = await res.json();

  document.getElementById("name").value = user.name || "";
  document.getElementById("email").value = user.email || "";
  document.getElementById("style").value = user.style || "Casual";
  document.getElementById("climate").value = user.climate || "Moderate";
}

document.addEventListener("DOMContentLoaded", loadProfile);

const form = document.querySelector(".profile-form");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      style: document.getElementById("style").value,
      climate: document.getElementById("climate").value
    };
    await fetch("/profile/save", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    alert("✅ Profile Saved!");
  });
}
