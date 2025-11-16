document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("accessories-grid");
    const empty = document.getElementById("empty-accessories");
    const form = document.getElementById("addAccessoryForm");

    let accessories = [];

    async function loadAccessories(filter = "all") {
        const res = await fetch("/api/accessories");
        accessories = await res.json();

        const filtered = filter === "all" ? accessories : accessories.filter(a => a.type === filter);

        grid.innerHTML = "";

        if (filtered.length === 0) {
            empty.style.display = "";
            return;
        }
        empty.style.display = "none";

        filtered.forEach(acc => {
            const card = document.createElement("div");
            card.className = "col-md-4";

            let icon = "👜"; // default
            switch (acc.type) {
                case "Jewellery": icon = "📿"; break; 
                case "Purse": icon = "👜"; break;     
                case "Hat": icon = "🎩"; break;      
                case "Utility": icon = "☂️"; break;  
                case "Belt": icon = "🧷"; break;      
                case "Watch": icon = "⌚"; break;      
                case "Scarf": icon = "🧣"; break;   
                case "Sunglasses": icon = "🕶️"; break; 
            }

            card.innerHTML = `
        <div class="wardrobe-item-card">
          <div class="wardrobe-item-image">${icon}</div>
          <div class="wardrobe-item-title">${acc.name}</div>
          <div class="wardrobe-item-meta">${acc.type}</div>
          <button class="wardrobe-item-btn" data-id="${acc.id}">Remove</button>
        </div>
      `;
            grid.appendChild(card);

            card.querySelector(".wardrobe-item-btn").addEventListener("click", async () => {
                await fetch(`/api/accessories/${acc.id}`, { method: "DELETE" });
                loadAccessories(document.querySelector(".filter-chip.filter-active").dataset.filter);
            });
        });
    }

    // Setup filters
    document.querySelectorAll(".filter-chip").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelector(".filter-chip.filter-active").classList.remove("filter-active");
            btn.classList.add("filter-active");
            loadAccessories(btn.dataset.filter);
        });
    });

    // Add accessory
    form.addEventListener("submit", async e => {
        e.preventDefault();
        const name = document.getElementById("accName").value;
        const type = document.getElementById("accType").value;

        await fetch("/api/accessories", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, type })
        });

        bootstrap.Modal.getInstance(document.getElementById("addAccessoryModal")).hide();
        form.reset();
        loadAccessories(document.querySelector(".filter-chip.filter-active").dataset.filter);
    });

    loadAccessories(); // initial load
});
