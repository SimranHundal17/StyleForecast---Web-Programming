// static/profile.js

async function loadProfile() {
  const res = await fetch("/profile/profile/data");
  const user = await res.json();

  document.getElementById("name").value = user.name || "";
  document.getElementById("email").value = user.email || "";
  document.getElementById("style").value = user.style || "Casual";
  document.getElementById("climate").value = user.climate || "Moderate";
}

document.addEventListener("DOMContentLoaded", loadProfile);

// colors used for avatar backgrounds
const avatarColors = [
  "#6366F1",
  "#EC4899",
  "#F59E0B",
  "#10B981",
  "#3B82F6"
];

// returns initials from full name
function getInitials(fullName) {
  if (!fullName) return "?";
  const parts = fullName.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

// picks stable color based on name hash
function pickColorFromName(name) {
  if (!name) return avatarColors[0];
  let sum = 0;
  for (let i = 0; i < name.length; i++) {
    sum += name.charCodeAt(i);
  }
  return avatarColors[sum % avatarColors.length];
}

// updates the avatar circle UI
function updateProfileAvatar() {
  const nameInput = document.getElementById("name");
  const avatar = document.getElementById("profileAvatar");

  if (!nameInput || !avatar) return;

  const name = nameInput.value.trim();
  avatar.textContent = getInitials(name);
  avatar.style.backgroundColor = pickColorFromName(name);
}

// run avatar update when profile loads
document.addEventListener("DOMContentLoaded", updateProfileAvatar);

// update live while typing
const nameInput = document.getElementById("name");
if (nameInput) {
  nameInput.addEventListener("input", updateProfileAvatar);
}

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