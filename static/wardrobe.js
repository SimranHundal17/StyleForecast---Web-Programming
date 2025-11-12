// static/wardrobe.js

let currentFilter = "all";

/**
 * Load wardrobe items from backend with optional filter.
 * @param {string} filter - 'all' | 'needs' | 'clean' | category name
 */
async function loadWardrobe(filter = currentFilter) {
  currentFilter = filter || "all";
  const res = await fetch(`/wardrobe/data?filter=${encodeURIComponent(currentFilter)}`);
  const items = await res.json();

  const grid = document.querySelector(".wardrobe-items-section .row");
  if (!grid) return;
  grid.innerHTML = "";

  items.forEach((item) => {
    const btnLabel = (item.status || "").toLowerCase() === "clean" ? "Mark as Worn" : "Mark as Clean";
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

/**
 * Toggle item status and reload with the same filter.
 */
async function updateItemStatus(id) {
  await fetch("/wardrobe/update", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ id })
  });
  await loadWardrobe(currentFilter);
}

/**
 * Wire up filter chips: add active class and reload.
 */
function setupFilterChips() {
  const chips = document.querySelectorAll(".filter-chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("filter-active"));
      chip.classList.add("filter-active");
      const value = chip.getAttribute("data-filter") || "all";
      loadWardrobe(value);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupFilterChips();
  loadWardrobe("all");
});
