// Load and render outfit history cards
async function loadHistory() {
  try {
    const res = await fetch("/outfit_history/data");
    const history = await res.json();

    const grid = document.querySelector(".history-items-section .row");
    const empty = document.querySelector(".empty-state");

    if (!grid) return;

    grid.innerHTML = "";

    if (!history || history.length === 0) {
      if (empty) empty.classList.remove("d-none");
      return;
    }

    if (empty) empty.classList.add("d-none");

    history.forEach((entry) => {
      const outfitText = Array.isArray(entry.outfit)
        ? entry.outfit.join(", ")
        : entry.outfit || "";

      // build card HTML (similar to wardrobe)
      grid.innerHTML += `
        <div class="col-md-4">
          <div class="history-item-card">
            <div class="history-item-date">
              ${entry.date || ""} • ${entry.location || ""}${
                entry.weather ? " • " + entry.weather : ""
              }
            </div>
            <div class="history-item-outfit">${outfitText}</div>
            <div class="history-item-meta">
              Mood: ${entry.mood || "—"} • Rating: ${entry.rating ?? "—"}
              ${entry.liked ? " • ❤️ Liked" : ""}
            </div>
            <button 
              class="history-item-btn" 
              data-id="${entry.id}">
              Remove
            </button>
          </div>
        </div>
      `;
    });

    // attach click handlers for remove buttons
    const removeButtons = grid.querySelectorAll(".history-item-btn");
    removeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        deleteHistoryEntry(id); // no confirm dialog
      });
    });
  } catch (e) {
    console.error("Failed to load history:", e);
  }
}

// Call API to delete one history entry
async function deleteHistoryEntry(id) {
  try {
    const res = await fetch(`/outfit_history/api/delete/${id}`, {
      method: "DELETE",
    });

    const data = await res.json();

    if (!data.ok) {
      console.error("Failed to delete history entry");
      return;
    }

    // reload list after delete
    await loadHistory();
  } catch (e) {
    console.error("Failed to delete history entry:", e);
  }
}

// Init on DOM ready
document.addEventListener("DOMContentLoaded", loadHistory);
