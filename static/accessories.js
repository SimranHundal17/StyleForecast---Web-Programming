document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("accessories-grid");
    const empty = document.getElementById("empty-accessories");
    const form = document.getElementById("addAccessoryForm");

    async function loadAccessories(filter = "all") {
        const res = await fetch("/accessories/api/accessories", { credentials: "include" });
        const accessories = await res.json();

        let filtered = filter === "all" ? accessories : accessories.filter(a => a.type === filter);

        grid.innerHTML = "";

        if (filtered.length === 0) {
            empty.style.display = "block";
            return;
        }
        empty.style.display = "none";

        filtered.forEach(acc => {
            const card = document.createElement("div");
            card.className = "col-md-4";

            let icons = {
                "Jewellery": "📿",
                "Purse": "👜",
                "Hat": "🎩",
                "Utility": "☂️",
                "Belt": "🧷",
                "Watch": "⌚",
                "Scarf": "🧣",
                "Sunglasses": "🕶️"
            };

            const icon = icons[acc.type] || "👜";

            card.innerHTML = `
                <div class="wardrobe-item-card">
                    <div class="wardrobe-item-image">${icon}</div>
                    <div class="wardrobe-item-title">${acc.name}</div>
                    <div class="wardrobe-item-meta">${acc.type}</div>
                    <button class="wardrobe-item-btn" data-id="${acc._id}">Remove</button>
                </div>
            `;

            card.querySelector(".wardrobe-item-btn").addEventListener("click", async () => {
                await fetch(`/accessories/api/accessories/${acc._id}`, {
                    method: "DELETE",
                    credentials: "include"
                });
                loadAccessories(filter);
            });

            grid.appendChild(card);
        });
    }

    // Filters
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

        await fetch("/accessories/api/accessories", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, type })
        });

        bootstrap.Modal.getInstance(document.getElementById("addAccessoryModal")).hide();
        form.reset();
        loadAccessories();
    });

    loadAccessories();
});
