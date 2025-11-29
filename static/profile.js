// static/profile.js

// colors used for avatar backgrounds
const avatarColors = [
  "#6366F1",
  "#EC4899",
  "#F59E0B",
  "#10B981",
  "#3B82F6",
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
document.addEventListener("DOMContentLoaded", () => {
  updateProfileAvatar();
});

// update live while typing
const nameInput = document.getElementById("name");
if (nameInput) {
  nameInput.addEventListener("input", updateProfileAvatar);
}

const form = document.querySelector(".profile-form");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // payload that will be sent to /profile/update
    const data = {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      name: `${document.getElementById("first_name").value} ${document.getElementById("last_name").value}`.trim(),
      email: document.getElementById("email").value,
      password: document.getElementById("password").value,
      confirm_password: document.getElementById("confirm_password").value,
      gender: document.getElementById("gender").value,
      age: document.getElementById("age").value,
      days_until_dirty: document.getElementById("days_until_dirty").value
    };

    try {
      const res = await fetch("/profile/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const json = await res.json();
      console.log("Profile updated:", json);    
    } catch (err) {
      console.error("Failed to update profile:", err);
    }
  });
}
