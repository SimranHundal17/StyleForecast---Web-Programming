async function loadHistory() {
  try {
    const res = await fetch("/history/data");
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

    history.forEach(entry => {
      const outfitText = Array.isArray(entry.outfit)
        ? entry.outfit.join(", ")
        : (entry.outfit || "");

      grid.innerHTML += `
        <div class="col-md-4">
          <div class="history-item-card">
            <div class="history-item-date">${entry.date} • ${entry.location || ""} ${entry.weather ? "• " + entry.weather : ""}</div>
            <div class="history-item-outfit">${outfitText}</div>
            <div class="history-item-meta">
              Occasion: ${entry.occasion || "—"} • Mood: ${entry.mood || "—"} • Rating: ${entry.rating ?? "—"}
              ${entry.liked ? " • ❤️ Liked" : ""}
            </div>
          </div>
        </div>
      `;
    });
  } catch (e) {
    console.error("Failed to load history:", e);
  }
}

document.addEventListener("DOMContentLoaded", loadHistory);
