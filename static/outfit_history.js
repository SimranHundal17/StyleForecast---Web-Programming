// Load and render outfit history cards
// This function gets outfit history from backend and shows it on the page
async function loadHistory() {
  try {
    // Request history data from server
    const res = await fetch("/outfit_history/data");
    const history = await res.json();

    // Find grid where cards will be rendered
    const grid = document.getElementById("history-grid") || document.querySelector(".history-items-section .row");

    // Find empty state block
    const empty = document.getElementById("empty-state") || document.querySelector(".empty-state");

    // If grid is not found, stop execution
    if (!grid) return;

    // Clear previous content
    grid.innerHTML = "";

    // If history is empty or invalid, show empty state
    if (!Array.isArray(history) || history.length === 0) {
      if (empty) empty.classList.remove("d-none");
      return;
    }

    // Hide empty state when data exists
    if (empty) empty.classList.add("d-none");

    // Emoji mapping for occasion values
    const occasionEmoji = {
      Casual: "👕",
      Formal: "👔",
      Party: "🎉",
      Gym: "🏋️",
      Rainy: "☔",
    };

    // Order of clothing roles for display
    const roleOrder = { top: 1, onepiece: 2, bottom: 3, outer: 4, shoes: 5 };

    // Escape HTML to prevent XSS attacks
    const escapeHtml = (value) => {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
    };

    // Remove emoji or symbols from start of text
    const stripLeadingEmoji = (text) => {
      const s = String(text ?? "").trim();
      return s.replace(/^[^A-Za-z0-9]+\s*/, "");
    };

    // Format one outfit item label
    const formatItemLabel = (it) => {
      // If item is already a string
      if (typeof it === "string") {
        return stripLeadingEmoji(it);
      }

      // Extract name and color from object
      const nameRaw = it?.name || it?.role || "";
      const name = stripLeadingEmoji(nameRaw);
      const color = String(it?.color || "").trim();

      if (!name) return "";
      if (!color) return name;

      // Avoid duplicating color name
      const lowerName = name.toLowerCase();
      const lowerColor = color.toLowerCase();
      if (lowerName.startsWith(lowerColor + " ")) return name;

      return `${color} ${name}`;
    };

    // Format full outfit text for one history entry
    const formatOutfitText = (entry) => {
      if (!Array.isArray(entry?.outfit)) return entry?.outfit || "";

      const items = entry.outfit
        .slice()
        // Sort items by clothing role order
        .sort((a, b) => {
          const ra = typeof a === "object" && a ? String(a.role || "").toLowerCase() : "";
          const rb = typeof b === "object" && b ? String(b.role || "").toLowerCase() : "";
          return (roleOrder[ra] || 99) - (roleOrder[rb] || 99);
        })
        // Convert items to readable text
        .map(formatItemLabel)
        .filter(Boolean);

      return items.join(", ");
    };

    // Render each history entry as a card
    history.forEach((entry) => {
      const outfitText = formatOutfitText(entry);
      const occ = String(entry.occasion || "—");
      const occIcon = occasionEmoji[occ] || "✨";
      const weatherText = entry.weather ? ` • ${entry.weather}` : "";

      // Insert card HTML into grid
      grid.insertAdjacentHTML(
        "beforeend",
        `
        <div class="col-md-4">
          <div class="history-item-card">
            <div class="history-item-body">
              <div class="history-item-date">
                ${escapeHtml(entry.date || "")} • ${escapeHtml(entry.location || "")}${escapeHtml(weatherText)}
              </div>
              <div class="history-item-outfit">${escapeHtml(outfitText)}</div>
              <div class="history-item-meta">
                Occasion: ${escapeHtml(occIcon)} ${escapeHtml(occ)}
              </div>
            </div>
            <div class="history-item-footer">
              <button class="history-item-btn" data-id="${escapeHtml(entry.id)}">
                Remove
              </button>
            </div>
          </div>
        </div>
        `
      );
    });

    // Add click handlers for remove buttons
    const removeButtons = grid.querySelectorAll(".history-item-btn");
    removeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        deleteHistoryEntry(id);
      });
    });

  } catch (e) {
    // Log error if loading fails
    console.error("Failed to load history:", e);
  }
}

// Call API to delete one history entry by ID
async function deleteHistoryEntry(id) {
  try {
    // Send DELETE request to backend
    const res = await fetch(`/outfit_history/api/delete/${id}`, {
      method: "DELETE",
    });

    const data = await res.json();

    // If deletion failed, log error
    if (!data.ok) {
      console.error("Failed to delete history entry");
      return;
    }

    // Reload history list after deletion
    await loadHistory();
  } catch (e) {
    console.error("Failed to delete history entry:", e);
  }
}

// Initialize history loading when page is ready
document.addEventListener("DOMContentLoaded", loadHistory);