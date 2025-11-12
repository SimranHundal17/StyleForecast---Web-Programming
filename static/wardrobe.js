async function loadWardrobe() {
  const res = await fetch("/wardrobe/data");
  const items = await res.json();

  // Hide "empty" if there are items
  const empty = document.querySelector(".empty-state");
  if (empty) {
    if (items && items.length) empty.classList.add("d-none");
    else empty.classList.remove("d-none");
  }

  const grid = document.querySelector(".wardrobe-items-section .row");
  if (!grid) return;
  grid.innerHTML = "";

  items.forEach((item) => {
    const btnLabel = item.status === "Clean" ? "Mark as worn" : "Mark as clean";
    grid.innerHTML += `
      <div class="col-md-4">
        <div class="wardrobe-item-card">
          <div class="wardrobe-item-image">${item.icon || "👕"}</div>
          <div class="wardrobe-item-title">${item.name}</div>
          <div class="wardrobe-item-meta">${item.category} • ${item.status}</div>
          <button class="wardrobe-item-btn" onclick="updateItemStatus(${item.id})">
            ${btnLabel}
          </button>
        </div>
      </div>
    `;
  });
}

async function updateItemStatus(id) {
  await fetch("/wardrobe/update", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ id })
  });
  loadWardrobe();
}

document.addEventListener("DOMContentLoaded", loadWardrobe);
