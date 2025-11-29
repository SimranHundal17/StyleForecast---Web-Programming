// static/outfit_history.js

// load and render history cards from backend
async function loadHistory() {
  try {
    const res = await fetch("/outfit_history/data");
    const history = await res.json();

    const grid = document.querySelector(".history-items-section .row");
    const empty = document.querySelector(".empty-state");

    if (!grid) return;

    // clear grid before rendering
    grid.innerHTML = "";

    // show empty state if no history
    if (!history || history.length === 0) {
      if (empty) empty.classList.remove("d-none");
      return;
    }

    if (empty) empty.classList.add("d-none");

    history.forEach((entry) => {
      const outfitText = Array.isArray(entry.outfit)
        ? entry.outfit.join(", ")
        : entry.outfit || "";

      grid.innerHTML += `
        <div class="col-md-4">
          <div class="history-item-card">
            <div class="history-item-date">
              ${entry.date || ""} • ${entry.location || ""} ${
        entry.weather ? "• " + entry.weather : ""
      }
            </div>
            <div class="history-item-outfit">${outfitText}</div>
            <div class="history-item-meta">
              Mood: ${entry.occasion || "—"
      } • Rating: ${entry.rating ?? "—"}
              ${entry.liked ? " • ❤️ Liked" : ""}
            </div>
            <div class="history-item-actions mt-2">
              <button 
                class="history-item-btn history-remove-btn" 
                data-id="${entry.id}">
                Remove
              </button>
            </div>
          </div>
        </div>
      `;
    });
  } catch (e) {
    console.error("Failed to load history:", e);
  }
}

// delete single history entry by id
async function deleteHistoryEntry(id) {
  try {
    const res = await fetch(`/outfit_history/api/delete/${id}`, {
      method: "DELETE",
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();

    if (data.ok) {
      // reload list after delete
      await loadHistory();
    } else {
      alert("Failed to delete entry.");
    }
  } catch (e) {
    console.error("Failed to delete history entry:", e);
    alert("Failed to delete entry. Please try again.");
  }
}

// setup click handler for remove buttons (event delegation)
function setupHistoryActions() {
  const grid = document.querySelector(".history-items-section .row");
  if (!grid) return;

  grid.addEventListener("click", (e) => {
    const btn = e.target.closest(".history-remove-btn");
    if (!btn) return;

    const id = btn.dataset.id;
    if (!id) return;

    // optional confirm
    if (confirm("Remove this outfit from history?")) {
      deleteHistoryEntry(id);
    }
  });
}

// init on page load
document.addEventListener("DOMContentLoaded", () => {
  setupHistoryActions();
  loadHistory();
});
