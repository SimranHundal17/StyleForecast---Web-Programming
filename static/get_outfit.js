// ======================================================
// DOM ELEMENTS
// ======================================================
const locationInput = document.getElementById("locationInput");
const suggestionsBox = document.getElementById("locationSuggestions");
const spinner = document.getElementById("loadingSpinner");
const previewBox = document.getElementById("outfitPreview");
const generateBtn = document.getElementById("generateOutfitBtn");

const feedbackButtons = document.getElementById("feedbackButtons");
const ratingBox = document.getElementById("ratingBox");
const saveMessage = document.getElementById("saveMessage");

const likeBtn = document.getElementById("likeBtn");
const dislikeBtn = document.getElementById("dislikeBtn");

let selectedLat = null;
let selectedLon = null;
let lastGenerated = null;
let autocompleteTimeout = null;


// ======================================================
// AUTOCOMPLETE
// ======================================================
locationInput.addEventListener("input", () => {
    const query = locationInput.value.trim();
    suggestionsBox.innerHTML = "";

    selectedLat = null;
    selectedLon = null;
    generateBtn.disabled = true;

    clearTimeout(autocompleteTimeout);
    if (!query) return;

    autocompleteTimeout = setTimeout(async () => {
        const url = `/get_outfit/api/location/autocomplete?q=${encodeURIComponent(query)}`;

        const response = await fetch(url, { credentials: "include" });
        const results = await response.json();

        suggestionsBox.innerHTML = "";

        if (results.length === 0) {
            const div = document.createElement("div");
            div.className = "autocomplete-item text-danger";
            div.textContent = "Location not found";
            suggestionsBox.appendChild(div);
            return;
        }

        results.forEach(item => {
            const div = document.createElement("div");
            div.className = "autocomplete-item";
            div.textContent = item.label;

            div.addEventListener("click", () => {
                locationInput.value = item.label;
                selectedLat = item.lat;
                selectedLon = item.lon;

                suggestionsBox.innerHTML = "";
                generateBtn.disabled = false;
            });

            suggestionsBox.appendChild(div);
        });
    }, 250);
});


// Close dropdown
document.addEventListener("click", e => {
    if (!locationInput.contains(e.target)) {
        suggestionsBox.innerHTML = "";
    }
});


// ======================================================
// AUTO-DETECT LOCATION
// ======================================================
window.addEventListener("DOMContentLoaded", () => {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        const url = `/get_outfit/api/location/reverse?lat=${lat}&lon=${lon}`;
        const response = await fetch(url, { credentials: "include" });
        const data = await response.json();

        if (!data.error) {
            locationInput.value = data.label;
            selectedLat = data.lat;
            selectedLon = data.lon;
            generateBtn.disabled = false;
        }
    });
});


// ======================================================
// GENERATE OUTFIT
// ======================================================
generateBtn.addEventListener("click", async () => {
    if (!selectedLat || !selectedLon) return;

    const occasion = document.getElementById("occasionInput").value;

    spinner.classList.remove("d-none");
    previewBox.innerHTML = "";
    saveMessage.classList.add("d-none");
    feedbackButtons.style.display = "none";
    ratingBox.classList.add("d-none");

    const response = await fetch("/get_outfit/api/get_outfit", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: selectedLat,
            lon: selectedLon,
            occasion
        })
    });

    const data = await response.json();
    spinner.classList.add("d-none");

    if (data.error) {
        previewBox.innerHTML = `<div class="text-danger">${data.error}</div>`;
        return;
    }

    // Update weather UI
    document.getElementById("weatherTemp").textContent = `${data.temp}°C`;
    document.getElementById("weatherDesc").textContent = data.condition;
    document.getElementById("weatherLocation").textContent = locationInput.value;
    document.getElementById("weatherFull").textContent = data.weather;

    let icon = "☁️";
    if (data.condition.includes("Rain")) icon = "🌧️";
    if (data.condition.includes("Clear")) icon = "☀️";
    if (data.condition.includes("Snow")) icon = "❄️";

    document.getElementById("weatherIcon").textContent = icon;

    // Outfit preview
    previewBox.innerHTML = "";
    data.outfit.forEach(item => {
        const div = document.createElement("div");
        div.className = "outfit-item";
        div.textContent = item;
        previewBox.appendChild(div);
    });

    lastGenerated = {
        location: locationInput.value,
        weather: data.weather,
        occasion,
        outfit: data.outfit
    };

    feedbackButtons.style.display = "block";
});


// ======================================================
// DISLIKE → regenerate
// ======================================================
dislikeBtn.addEventListener("click", () => {
    generateBtn.click();
});


// ======================================================
// LIKE → show rating only (do not save yet)
// ======================================================
likeBtn.addEventListener("click", () => {
    ratingBox.classList.remove("d-none");
});


// ======================================================
// If user clicks LIKE again → save with rating = null
// ======================================================
likeBtn.addEventListener("dblclick", async () => {
    if (!lastGenerated) return;

    if (!ratingBox.classList.contains("d-none")) {
        const res = await fetch("/get_outfit/api/save_outfit", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ...lastGenerated, rating: null })
        });

        const result = await res.json();
        if (result.success) {
            saveMessage.textContent = "Outfit saved (no rating)";
            saveMessage.classList.remove("d-none");
        }

        ratingBox.classList.add("d-none");
    }
});


// ======================================================
// STAR RATING → final save
// ======================================================
document.querySelectorAll("#starsContainer span").forEach(star => {
    star.addEventListener("click", async () => {
        const rating = star.dataset.v;

        const res = await fetch("/get_outfit/api/save_outfit", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ...lastGenerated, rating })
        });

        const result = await res.json();
        if (result.success) {
            saveMessage.textContent = "Outfit saved with rating!";
            saveMessage.classList.remove("d-none");
        }

        ratingBox.classList.add("d-none");
    });
});
