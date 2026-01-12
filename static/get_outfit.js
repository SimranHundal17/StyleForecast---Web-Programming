// ======================================================
// static/get_outfit.js — Client-side behavior for the Get Outfit page
// ======================================================
// Purpose: handle location autocomplete, optional browser geolocation,
// outfit generation via server API, preview rendering, and saving to history.
// Exam notes:
// - Autocomplete is debounced (250ms) to avoid excessive API calls while typing.
// - All fetch calls include `{ credentials: "include" }` so server-side session/JWT cookies
//   are sent with requests (important for authenticated endpoints).
// - Server responses used here are expected to include fields like:
//     { temp, condition, weather, outfit: Array<string> }
// - Like = save (POST to server), Dislike = regenerate (clicks generate again).
// Key DOM IDs: `locationInput`, `locationSuggestions`, `generateOutfitBtn`,
// `loadingSpinner`, `outfitPreview`, `feedbackButtons`, `likeBtn`, `dislikeBtn`.


// ======================================================
// DOM ELEMENTS
// ======================================================
const locationInput = document.getElementById("locationInput");
const suggestionsBox = document.getElementById("locationSuggestions");
const spinner = document.getElementById("loadingSpinner");
const previewBox = document.getElementById("outfitPreview");
const generateBtn = document.getElementById("generateOutfitBtn");

const feedbackButtons = document.getElementById("feedbackButtons");
const saveMessage = document.getElementById("saveMessage");

const likeBtn = document.getElementById("likeBtn");
const dislikeBtn = document.getElementById("dislikeBtn");

// These variables hold the selected coordinates and the last generated outfit
let selectedLat = null;
let selectedLon = null;
let lastGenerated = null;
// Used by the autocomplete debounce; cleared on subsequent keystrokes
let autocompleteTimeout = null;


// ======================================================
// AUTOCOMPLETE
// ======================================================
locationInput.addEventListener("input", () => {
    const query = locationInput.value.trim();
    suggestionsBox.innerHTML = "";

    // Reset selected coordinates when the text changes — user must click an autocomplete item
    selectedLat = null;
    selectedLon = null;
    generateBtn.disabled = true;

    // Debounce: clear any pending request and schedule a new one after 250ms.
    // This prevents excessive server calls while the user is still typing.
    clearTimeout(autocompleteTimeout);
    if (!query) return;

    autocompleteTimeout = setTimeout(async () => {
        const url = `/get_outfit/api/location/autocomplete?q=${encodeURIComponent(query)}`;

        // Use credentials to ensure session auth (cookies/JWT) is sent with the request.
        const response = await fetch(url, { credentials: "include" });
        const results = await response.json();

        suggestionsBox.innerHTML = "";

        if (!Array.isArray(results) || results.length === 0) {
            const div = document.createElement("div");
            div.className = "autocomplete-item text-danger";
            div.textContent = "Location not found";
            suggestionsBox.appendChild(div);
            return;
        }

        // Each result is expected to be like { label, lat, lon }
        results.forEach(item => {
            const div = document.createElement("div");
            div.className = "autocomplete-item";
            div.textContent = item.label;

            div.addEventListener("click", () => {
                // Selecting an item fills the input and stores coordinates for generation
                locationInput.value = item.label;
                selectedLat = item.lat;
                selectedLon = item.lon;

                suggestionsBox.innerHTML = "";
                generateBtn.disabled = false;
            });

            suggestionsBox.appendChild(div);
        });
    }, 250); // 250ms debounce window
});


// Close dropdown when clicking outside the input/suggestions area
document.addEventListener("click", e => {
    if (!locationInput.contains(e.target)) {
        suggestionsBox.innerHTML = "";
    }
});


// ======================================================
// AUTO-DETECT LOCATION
// ======================================================
window.addEventListener("DOMContentLoaded", () => {
    // Try to auto-detect user's location (permission may be denied)
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // reverse geocode via server endpoint to get a human-readable label
        const url = `/get_outfit/api/location/reverse?lat=${lat}&lon=${lon}`;
        const response = await fetch(url, { credentials: "include" });
        const data = await response.json();

        // Expect { label, lat, lon } or an { error } object
        if (!data.error) {
            locationInput.value = data.label;
            selectedLat = data.lat;
            selectedLon = data.lon;
            generateBtn.disabled = false;
        }
    }, err => {
        // If geolocation fails (permission denied or timeout), do nothing — user can type a location
        // No action required here, but this is where you'd handle errors if desired.
    });
});


// ======================================================
// GENERATE OUTFIT
// ======================================================
generateBtn.addEventListener("click", async () => {
    // Ensure coordinates are available (user must select an autocomplete item or allow geolocation)
    if (!selectedLat || !selectedLon) return;

    const occasion = document.getElementById("occasionInput").value;

    // Show spinner and clear previous preview/state
    spinner.classList.remove("d-none");
    previewBox.innerHTML = "";
    saveMessage.classList.add("d-none");
    feedbackButtons.style.display = "none";

    // Call server API to generate an outfit. Server needs lat/lon and optional occasion.
    const response = await fetch("/get_outfit/api/get_outfit", {
        method: "POST",
        credentials: "include", // important to include auth cookies/session
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: selectedLat,
            lon: selectedLon,
            occasion
        })
    });

    const data = await response.json();
    // Stop spinner after response received
    spinner.classList.add("d-none");

    // Server can return { error } on failure
    if (data.error) {
        previewBox.innerHTML = `<div class="text-danger">${data.error}</div>`;
        return;
    }

    // --- Weather UI updates ---
    // Expect fields like data.temp, data.condition, data.weather (a fuller string)
    document.getElementById("weatherTemp").textContent = `${data.temp}°C`;
    document.getElementById("weatherDesc").textContent = data.condition;
    document.getElementById("weatherLocation").textContent = locationInput.value;
    document.getElementById("weatherFull").textContent = data.weather;

    // Map a simple weather condition to an emoji icon for quick visual feedback
    let icon = "☁️";
    if (data.condition.includes("Rain")) icon = "🌧️";
    if (data.condition.includes("Clear")) icon = "☀️";
    if (data.condition.includes("Snow")) icon = "❄️";

    document.getElementById("weatherIcon").textContent = icon;

    // --- Outfit preview ---
    // Expect data.outfit to be an array of strings; render each item
    previewBox.innerHTML = "";
    (data.outfit || []).forEach(item => {
        const div = document.createElement("div");
        div.className = "outfit-item";
        div.textContent = item;
        previewBox.appendChild(div);
    });

    // Save the relevant metadata locally so the Like button can save it later
    lastGenerated = {
        location: locationInput.value,
        weather: data.weather,
        occasion,
        outfit: data.outfit
    };

    // Show like/dislike controls to gather quick feedback
    feedbackButtons.style.display = "block";
});


// ======================================================
// DISLIKE → regenerate
// ======================================================
// Dislike simply triggers generation again — keeps current coords/occasion
dislikeBtn.addEventListener("click", () => {
    generateBtn.click();
});


// ======================================================
// LIKE → save immediately
// ======================================================
// Like saves the currently shown outfit to the user's history. The server expects
// a payload like { location, weather, occasion, outfit, rating } — here `rating` is
// set to null to indicate a positive save without an explicit numeric score.
likeBtn.addEventListener("click", async () => {
    if (!lastGenerated) return;

    const res = await fetch("/get_outfit/api/save_outfit", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            ...lastGenerated,
            rating: null
        })
    });

    const result = await res.json();

    // Show a confirmation message on successful save
    if (result.success) {
        saveMessage.textContent = "Outfit saved to history!";
        saveMessage.classList.remove("d-none");
    }
});

