/* ============================================================
   static/plan_ahead.js — Plan-Ahead page client behavior
   ===========================================================
   Purpose: Allow users to plan outfits across single or multi-day ranges.
   Key concepts (exam notes):
   - Dates are represented as ISO date strings (YYYY-MM-DD) when stored and
     compared. Be mindful of local time vs UTC when converting Date objects.
   - savedPlans: the source of truth from the backend (persisted).
   - tempPlans: ephemeral plans generated during the session (not saved until
     user confirms). UI shows slider only for generated (temp) multi-day plans.
   - Slider is used only during generation; saved days always open single view.
   - Weather gaps: when the server cannot provide a forecast for a date,
     the UI marks the day as missingWeather and asks the user to select manually.
   - Server endpoints used by this file (examples):
     * GET /plan/plans -> [ { date, id, outfit, weather, ... } ]
     * POST /plan/create -> returns created plan(s) array
     * POST /plan/update -> accepts { id, outfit }
     * POST /plan/delete -> accepts { id }
   Notes: This file intentionally separates temp/saved state to avoid overwriting
   backend truth until the user explicitly saves. Do not change savedPlans
   directly when a plan is still temporary.
============================================================ */

/* -------------------- GLOBAL STATE ---------------------- */
let savedPlans = {};          // Real saved plans from backend
let tempPlans = {};          // Unsaved temporary plans during generation
let selectedDates = [];       // User-picked date range
let sliderDates = [];         // Used ONLY during generating
let currentSlideIndex = 0;

let selectedLat = null;
let selectedLon = null;
let userManuallySelectedLocation = false;

const today = new Date();

/* -------------------- DOM ---------------------- */
const planType = document.getElementById("planType");
const yearSelect = document.getElementById("yearSelect");
const monthSelect = document.getElementById("monthSelect");
const calendar = document.getElementById("calendar");
const planModal = new bootstrap.Modal(document.getElementById("planModal"));

const planInputSection = document.getElementById("planInputSection");
const singleDayContainer = document.getElementById("singleDayContainer");

const sliderContainer = document.getElementById("sliderContainer");
const slider = document.getElementById("slider");
const sliderDots = document.getElementById("sliderDots");
const loadingSpinner = document.getElementById("loadingSpinner");

const locationInput = document.getElementById("locationInput");
const suggestionsBox = document.getElementById("locationSuggestions");
const occasionInput = document.getElementById("occasionInput");
const weatherInput = document.getElementById("weatherInput");
const weatherAlert = document.getElementById("weatherAlert");
const generateBtn = document.getElementById("generateBtn");

/* ============================================================
   INITIAL LOAD
============================================================ */
async function loadSavedPlans() {
    // Fetch all saved plans from the server. Expected response is an array of
    // plan objects like { date: 'YYYY-MM-DD', id, outfit, weather, ... }.
    // Note: if your server requires cookies/session, you may need to include
    // `{ credentials: 'include' }` depending on auth setup.
    const res = await fetch("/plan/plans");
    const list = await res.json();

    // Rebuild savedPlans map for quick lookup by date
    savedPlans = {};
    list.forEach(p => savedPlans[p.date] = p);

    generateCalendar();
}

// Load saved plans on page load
loadSavedPlans();

/* ============================================================
   YEAR / MONTH OPTIONS
============================================================ */
for (let y = today.getFullYear(); y <= today.getFullYear() + 2; y++) {
    yearSelect.innerHTML += `<option value="${y}">${y}</option>`;
}
yearSelect.value = today.getFullYear();

[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
].forEach((m, i) => {
    monthSelect.innerHTML += `<option value="${i}">${m}</option>`;
});
monthSelect.value = today.getMonth();

yearSelect.addEventListener("change", generateCalendar);
monthSelect.addEventListener("change", generateCalendar);

/* ============================================================
   BUILD CALENDAR
============================================================ */
function generateCalendar() {
    calendar.innerHTML = "";

    const y = parseInt(yearSelect.value);
    const m = parseInt(monthSelect.value);

    // getDay(): 0 = Sunday, 1 = Monday, ...
    // We transform so Monday is the first column (0 = Monday)
    // (firstDay === 0 ? 6 : firstDay - 1) maps Sunday -> 6 and shifts others down.
    // Note: constructing `new Date(y, m, d)` uses local timezone; be careful with
    // comparisons if your backend stores dates in UTC.
    let firstDay = new Date(y, m, 1).getDay();
    firstDay = firstDay === 0 ? 6 : firstDay - 1;
    const lastDate = new Date(y, m + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
        calendar.appendChild(document.createElement("div"));
    }

    for (let d = 1; d <= lastDate; d++) {
        const div = document.createElement("div");
        div.className = "calendar-day";

        const dateStr = `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const dateObj = new Date(dateStr + "T00:00:00");
        const todayDateOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());

        div.textContent = d;

        if (dateObj < todayDateOnly) {
            div.classList.add("disabled");
        }

        /* Highlight saved future/today outfits */
        if (
            savedPlans[dateStr]?.outfit?.length > 0 &&
            dateObj >= todayDateOnly
        ) {
            div.classList.add("selected");
        }

        /* 🔥 Highlight TODAY always (even if selected) */
        if (
            dateObj.getTime() === todayDateOnly.getTime()
        ) {
            div.classList.add("today");
        }

        div.addEventListener("click", () => {
            if (!div.classList.contains("disabled")) onCalendarClick(dateStr);
        });

        calendar.appendChild(div);
    }
}

/* ============================================================
   DATE CLICK LOGIC — NO TRIP REOPENING
============================================================ */
function onCalendarClick(dateStr) {

    // 🔥 If this date already has a saved outfit (persisted in DB), always
    // open the saved single-day view (never re-open as a multi-day slider).
    // This preserves backend truth and prevents accidental overwrites.
    if (savedPlans[dateStr] && savedPlans[dateStr].id && savedPlans[dateStr].outfit?.length > 0) {
        openSavedSingleDay(dateStr);
        return;
    }

    // NEW SINGLE DAY
    if (planType.value === "one") {
        selectedDates = [dateStr];
        openModalForNew();
        return;
    }

    // MULTI-DAY: select start → end
    if (selectedDates.length === 0) {
        selectedDates = [dateStr];
        highlightRange();
        return;
    }

    if (selectedDates.length === 1) {
        const start = new Date(selectedDates[0]);
        const end = new Date(dateStr);

        selectedDates = [];
        let cur = new Date(Math.min(start, end));
        const fin = new Date(Math.max(start, end));

        while (cur <= fin) {
            selectedDates.push(cur.toISOString().split("T")[0]);
            cur.setDate(cur.getDate() + 1);
        }

        highlightRange();
        openModalForNew();
        return;
    }

    selectedDates = [dateStr];
    highlightRange();
}

/* ============================================================
   HIGHLIGHT TEMPORARY RANGE
============================================================ */
function highlightRange() {
    generateCalendar();

    document.querySelectorAll(".calendar-day").forEach(day => {
        const y = yearSelect.value;
        const m = monthSelect.value;
        const d = day.textContent;

        // Some cells are empty placeholders (no day text); skip them safely
        if (!d) return;

        // Build an ISO-style date string for comparison
        const dateStr = `${y}-${String(parseInt(m) + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;

        if (selectedDates.includes(dateStr)) {
            day.classList.add("range");
        }
    });
}

/* ============================================================
   OPEN NEW PLAN INPUT
============================================================ */
function openModalForNew() {
    tempPlans = {};
    sliderDates = [];
    currentSlideIndex = 0;

    planInputSection.classList.remove("d-none");
    singleDayContainer.classList.add("d-none");
    sliderContainer.classList.add("d-none");

    locationInput.value = "";
    suggestionsBox.innerHTML = "";
    generateBtn.disabled = true;

    // Reset coordinates & trigger auto-detect (unless user types their own location)
    selectedLat = selectedLon = null;
    userManuallySelectedLocation = false;

    autoDetectLocation();
    planModal.show();
}

/* ============================================================
   AUTO-DETECT LOCATION
============================================================ */
async function autoDetectLocation() {
    if (userManuallySelectedLocation) return;

    // Try to use browser geolocation; user may deny permission or it may fail.
    navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // Server reverse-geocoding endpoint should return { label, lat, lon } or { error }
        const res = await fetch(`/get_outfit/api/location/reverse?lat=${lat}&lon=${lon}`);
        const data = await res.json();

        if (!data.error) {
            locationInput.value = data.label;
            selectedLat = lat;
            selectedLon = lon;
            generateBtn.disabled = false;
        }
    });
}

/* ============================================================
   AUTOCOMPLETE LOCATION
============================================================ */
let autocompleteTimeout = null;

locationInput.addEventListener("input", () => {
    userManuallySelectedLocation = true;
    suggestionsBox.innerHTML = "";
    selectedLat = selectedLon = null;
    generateBtn.disabled = true;

    const q = locationInput.value.trim();
    clearTimeout(autocompleteTimeout);

    if (!q) return;

    // Debounced autocomplete (250ms) to reduce server load while typing.
    autocompleteTimeout = setTimeout(async () => {
        const res = await fetch(`/get_outfit/api/location/autocomplete?q=${encodeURIComponent(q)}`);
        const list = await res.json();

        suggestionsBox.innerHTML = "";

        if (!list.length) {
            suggestionsBox.innerHTML = `<div class="autocomplete-item text-danger">Not found</div>`;
            return;
        }

        // Each item is expected to have { label, lat, lon }
        list.forEach(item => {
            const div = document.createElement("div");
            div.className = "autocomplete-item";
            div.textContent = item.label;

            div.onclick = () => {
                // Selecting a suggestion stores coordinates used for generation
                locationInput.value = item.label;
                selectedLat = item.lat;
                selectedLon = item.lon;
                suggestionsBox.innerHTML = "";
                generateBtn.disabled = false;
            };

            suggestionsBox.appendChild(div);
        });
    }, 250);
});

/* ============================================================
   GENERATE BUTTON
============================================================ */
generateBtn.addEventListener("click", () => {

    if (!selectedLat || !selectedLon) {
        alert("Please select location first.");
        return;
    }

    if (planType.value === "one") {
        generateSingleDay();
        return;
    }

    generateMultiDay();
});

/* ============================================================
   GET WEATHER
============================================================ */
async function getWeatherFor(dateStr) {
    const res = await fetch(`/plan_ahead/api/weather_for_date?lat=${selectedLat}&lon=${selectedLon}&date=${dateStr}`);
    return await res.json();
}

/* ============================================================
   GENERATE SINGLE DAY — CLEAN TEMP BEFORE GENERATING
============================================================ */
async function generateSingleDay() {

    const date = selectedDates[0];

    // 🔥 Remove any transient fields from a previously saved plan so that
    // re-generation starts from a clean slate (prevents showing stale temp data).
    if (savedPlans[date]) {
        delete savedPlans[date].tempOutfit;
        delete savedPlans[date].outfit;
        delete savedPlans[date].weather;
        delete savedPlans[date].temp;
        delete savedPlans[date].description;
        delete savedPlans[date].missingWeather;
    }

    weatherAlert.classList.add("d-none");

    // If the user manually entered a weather override, we skip the getWeatherFor API
    // and pass the provided weather string to the get_outfit generation endpoint.

    const p = {
        date,
        location: locationInput.value,
        lat: selectedLat,
        lon: selectedLon,
        occasion: occasionInput.value
    };

    let weatherData;

    if (weatherInput.value) {
        weatherData = { weather: weatherInput.value, temp: null, description: null };
    } else {
        weatherData = await getWeatherFor(date);
    }

    if (weatherData.error) {
        weatherAlert.classList.remove("d-none");
        return;
    }

    const outfitData = await fetch("/get_outfit/api/get_outfit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: selectedLat,
            lon: selectedLon,
            occasion: p.occasion,
            weather: weatherData.weather
        })
    }).then(r => r.json());

    p.weather = weatherData.weather;
    p.temp = weatherData.temp;
    p.description = weatherData.description;
    p.tempOutfit = outfitData.outfit;

    tempPlans[date] = p;

    showGeneratedSingle(date);
}

/* ============================================================
   SHOW GENERATED SINGLE DAY
============================================================ */
function showGeneratedSingle(dateStr) {

    sliderContainer.classList.add("d-none");
    planInputSection.classList.add("d-none");
    singleDayContainer.classList.remove("d-none");

    const p = tempPlans[dateStr];

    document.querySelector(".sd-date").textContent = dateStr;
    document.querySelector(".sd-location").textContent = p.location;
    document.querySelector(".sd-occasion").textContent = p.occasion;
    document.querySelector(".sd-weather").textContent =
        `${p.weather}${p.temp ? ` (${p.temp}°C)` : ""}`;

    document.querySelector(".sd-outfit").innerHTML =
        p.tempOutfit.map(i => `<div class="outfit-item">${i}</div>`).join("");

    document.getElementById("singleBtnsNew").classList.remove("d-none");
    document.getElementById("singleBtnsSaved").classList.add("d-none");
    document.querySelectorAll(".sd-delete").forEach(b => b.classList.add("d-none"));

    document.querySelector(".sd-like").onclick =
        () => saveFinalOutfit(dateStr);

    document.querySelector(".sd-dislike").onclick =
        () => regenerateSingleDay(dateStr);

    bindDeleteButtons(dateStr);
}

/* ============================================================
   OPEN A SAVED SINGLE DAY
============================================================ */
function openSavedSingleDay(dateStr) {
    const p = savedPlans[dateStr];

    sliderContainer.classList.add("d-none");
    planInputSection.classList.add("d-none");
    singleDayContainer.classList.remove("d-none");

    document.querySelector(".sd-date").textContent = dateStr;
    document.querySelector(".sd-location").textContent = p.location;
    document.querySelector(".sd-occasion").textContent = p.occasion;
    document.querySelector(".sd-weather").textContent =
        `${p.weather}${p.temp ? ` (${p.temp}°C)` : ""}`;

    document.querySelector(".sd-outfit").innerHTML =
        p.outfit.map(i => `<div class="outfit-item">${i}</div>`).join("");

    document.getElementById("singleBtnsNew").classList.add("d-none");
    document.getElementById("singleBtnsSaved").classList.remove("d-none");

    document.querySelectorAll(".sd-delete").forEach(b => b.classList.remove("d-none"));

    document.querySelector(".sd-regenerate").onclick =
        () => regenerateSingleDay(dateStr);

    bindDeleteButtons(dateStr);

    planModal.show();
}

/* ============================================================
   REGENERATE = DELETE + GENERATE (CLEAN RESET)
============================================================ */
async function regenerateSingleDay(dateStr) {

    const saved = savedPlans[dateStr];

    // 1️⃣ If it exists in DB → delete it (same as delete button)
    if (saved?.id) {
        await fetch("/plan/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: saved.id })
        });
    }

    // 2️⃣ Remove from savedPlans → calendar unhighlights
    delete savedPlans[dateStr];
    generateCalendar();

    // 3️⃣ Treat as brand-new generation
    selectedDates = [dateStr];
    tempPlans = {};
    sliderDates = [];

    // 4️⃣ Re-generate like new
    await generateSingleDay();
}

/* ============================================================
   GENERATE MULTI-DAY — wipe temp before generating
============================================================ */
async function generateMultiDay() {

    slider.innerHTML = "";
    sliderDots.innerHTML = "";
    sliderContainer.classList.add("d-none");

    tempPlans = {};
    sliderDates = [];
    currentSlideIndex = 0;

    // 🔥 REMOVE ANY OLD TEMPORARY DATA
    sliderDates.forEach(d => {
        if (savedPlans[d]) {
            delete savedPlans[d].tempOutfit;
            delete savedPlans[d].outfit;
            delete savedPlans[d].weather;
            delete savedPlans[d].temp;
            delete savedPlans[d].description;
            delete savedPlans[d].missingWeather;
        }
    });

    sliderDates = [...selectedDates];
    planInputSection.classList.add("d-none");
    singleDayContainer.classList.add("d-none");
    sliderContainer.classList.remove("d-none");

    loadingSpinner.classList.remove("d-none");

    const results = {};
    const occasion = occasionInput.value;

// For each day in the slider, attempt to obtain weather and then an outfit.
        for (const d of sliderDates) {
        let weatherData;

        // Allow manual weather override for all generated days
        if (weatherInput.value) {
            weatherData = { weather: weatherInput.value, temp: null, description: null };
        } else {
            weatherData = await getWeatherFor(d);
        }

        let outfit = [];
        let missing = false;

        // If the weather API couldn't provide a forecast for this date, mark it missing
        if (weatherData.error) {
            missing = true;
        } else {
            // Call outfit-generation endpoint with lat/lon and the chosen weather
            const outfitData = await fetch("/get_outfit/api/get_outfit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    lat: selectedLat,
                    lon: selectedLon,
                    occasion,
                    weather: weatherData.weather
                })
            }).then(r => r.json());

            outfit = outfitData.outfit;
        }

        // Store results for later building of tempPlans and slider
        results[d] = {
            missingWeather: missing,
            weather: weatherData.weather,
            temp: weatherData.temp,
            description: weatherData.description,
            outfit
        };
    }

    sliderDates.forEach(date => {
        const r = results[date];

        tempPlans[date] = {
            date,
            location: locationInput.value,
            lat: selectedLat,
            lon: selectedLon,
            occasion,
            weather: r.weather,
            temp: r.temp,
            description: r.description,
            tempOutfit: r.outfit,
            missingWeather: r.missingWeather,
            id: null,
        };
    });

    loadingSpinner.classList.add("d-none");
    buildSlider();
    openSliderOn(sliderDates[0]);
}

/* ============================================================
   BUILD SLIDER — ONLY DURING GENERATION
============================================================ */
function buildSlider() {

    slider.innerHTML = "";
    sliderDots.innerHTML = "";

    sliderDates.forEach((date, idx) => {

        const p = tempPlans[date];
        const slide = document.createElement("div");
        slide.className = "slider-slide text-center";

        if (!p) {
            slide.innerHTML = `
            <h4>${date}</h4>
            <p class="text-success fw-bold">✔ Outfit saved</p>
            <p>You can continue to the next day.</p>
        `;
            slider.appendChild(slide);
        }
        else if (p.missingWeather) {
            // When weather is missing for a date, let the user pick weather manually
            // and re-generate for just that day via `regenerateMissing`.
            slide.innerHTML = `
            <h4>${date}</h4>
            <p class="text-danger fw-bold">Weather missing. Select manually:</p>
            <select class="form-select weather-select mx-auto" style="max-width:250px;">
                <option value="">Select Weather</option>
                <option value="Clear">Clear</option>
                <option value="Clouds">Clouds</option>
                <option value="Rain">Rain</option>
                <option value="Snow">Snow</option>
            </select>
            <button class="btn btn-primary regen-btn mt-2">Generate</button>
        `;
            slide.querySelector(".regen-btn").onclick =
                () => regenerateMissing(date, slide);
            slider.appendChild(slide);
        }
        else {
            // Normal generated slide: shows preview and provides Like/Dislike actions
            // Like saves this date's outfit to the backend (via saveFinalOutfit)
            // Dislike regenerates this single day (non-destructive to other days)
            slide.innerHTML = `
            <h4>${date}</h4>
            <p><b>Location:</b> ${p.location}</p>
            <p><b>Occasion:</b> ${p.occasion}</p>
            <p><b>Weather:</b> ${p.weather}${p.temp ? ` (${p.temp}°C)` : ""}</p>
            <div class="outfit-preview justify-content-center">
                ${p.tempOutfit.map(i => `<div class="outfit-item">${i}</div>`).join("")}
            </div>
            <div class="text-center mt-3">
                <button class="btn btn-success likeBtn me-2">👍 Like</button>
                <button class="btn btn-danger dislikeBtn me-2">👎 Dislike</button>
            </div>
        `;
            slide.querySelector(".likeBtn").onclick = () => saveFinalOutfit(date);
            slide.querySelector(".dislikeBtn").onclick = () => regenerateMultiDayOne(date);
            slider.appendChild(slide);
        }

        const dot = document.createElement("span");
        dot.className = "slider-dot";
        dot.textContent = "•";
        dot.onclick = () => {
            currentSlideIndex = idx;
            updateSliderPosition();
        };
        sliderDots.appendChild(dot);
    });


    updateSliderPosition();
}

/* ============================================================
   REGENERATE MISSING WEATHER (MULTI-DAY SLIDER)
============================================================ */
async function regenerateMissing(dateStr, slideElement) {

    // ✅ This must operate on tempPlans (ephemeral) — do NOT modify savedPlans here
    const p = tempPlans[dateStr];

    if (!p) {
        alert("Something went wrong. Please try again.");
        return;
    }

    const sel = slideElement.querySelector(".weather-select");
    const chosen = sel.value;

    if (!chosen) {
        alert("Select weather first.");
        return;
    }

    // Request a fresh outfit for the manually chosen weather and update temp-only state
    const outfitData = await fetch("/get_outfit/api/get_outfit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: p.lat,
            lon: p.lon,
            occasion: p.occasion,
            weather: chosen
        })
    }).then(r => r.json());

    // ✅ Update TEMP plan only
    p.weather = chosen;
    p.tempOutfit = outfitData.outfit;
    p.missingWeather = false;

    // 🔄 Rebuild slider UI and remain on the same date so the user can review
    buildSlider();
    openSliderOn(dateStr);
}

/* ============================================================
   REGENERATE ONE SLIDER DAY
============================================================ */
async function regenerateMultiDayOne(dateStr) {

    // NOTE: This operates on the persisted savedPlans entry — in some flows
    // you may prefer to operate on tempPlans if working within a generation session.
    const p = savedPlans[dateStr];

    const outfitData = await fetch("/get_outfit/api/get_outfit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: p.lat,
            lon: p.lon,
            occasion: p.occasion,
            weather: p.weather
        })
    }).then(r => r.json());

    // Apply regenerated outfit to the tempOutfit field so UI reflects the change
    p.tempOutfit = outfitData.outfit;

    buildSlider();
    openSliderOn(dateStr);
}

/* ============================================================
   OPEN SLIDER ON SPECIFIC DATE (GEN ONLY)
============================================================ */
function openSliderOn(dateStr) {
    currentSlideIndex = sliderDates.indexOf(dateStr);
    updateSliderPosition();
}

/* ============================================================
   UPDATE SLIDER POSITION
============================================================ */
function updateSliderPosition() {

    slider.style.transform = `translateX(-${currentSlideIndex * 100}%)`;

    [...sliderDots.children].forEach((dot, i) => {
        dot.style.color = (i === currentSlideIndex) ? "black" : "#bbb";
    });
}

document.getElementById("prevSlide").onclick = () => {
    if (currentSlideIndex > 0) {
        currentSlideIndex--;
        updateSliderPosition();
    }
};

document.getElementById("nextSlide").onclick = () => {
    if (currentSlideIndex < sliderDates.length - 1) {
        currentSlideIndex++;
        updateSliderPosition();
    }
};

/* ============================================================
   SAVE OUTFIT (SINGLE OR MULTI)
============================================================ */
async function saveFinalOutfit(dateStr) {

    const p = tempPlans[dateStr];
    const finalOutfit = p.tempOutfit;

    // ---------- CREATE PLAN IF NEEDED ----------
    // If the server hasn't created a plan entry yet, create one first
    if (!p.id) {
        const res = await fetch("/plan/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                start: dateStr,
                end: dateStr,
                location: p.location,
                lat: p.lat,
                lon: p.lon,
                occasion: p.occasion,
                weather: p.weather,
                temp: p.temp,
                description: p.description
            })
        });

        // The create endpoint returns an array of created plan objects (hence created[0].id)
        const created = await res.json();
        p.id = created[0].id;
    }

    // Save the outfit to the plan record
    await fetch("/plan/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id: p.id,
            outfit: finalOutfit
        })
    });

    // 🔥 Move the plan from temp -> saved and update the calendar so the day shows as persisted
    savedPlans[dateStr] = {
        ...p,
        outfit: finalOutfit
    };

    // 🔥 Remove temporary entry and refresh calendar UI
    delete tempPlans[dateStr];

    generateCalendar();

    /* =====================================================
       MULTI-DAY SLIDER LOGIC
    ===================================================== */
    if (sliderDates.length > 1) {

        if (currentSlideIndex < sliderDates.length - 1) {
            currentSlideIndex++;
            updateSliderPosition();
            return;
        }

        alert("Trip saved!");
        planModal.hide();
        return;
    }

    /* =====================================================
       SINGLE DAY LOGIC
    ===================================================== */
    alert("Saved!");
    planModal.hide();

}

/* ============================================================
   DELETE ONE DAY
============================================================ */
async function deletePlan(dateStr) {
    const p = savedPlans[dateStr];

    if (p?.id) {
        await fetch("/plan/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: p.id })
        });
    }

    delete savedPlans[dateStr];

    alert("Deleted.");
    planModal.hide();
    loadSavedPlans();
}

function bindDeleteButtons(dateStr) {
    document.querySelectorAll(".sd-delete").forEach(btn => {
        btn.onclick = () => deletePlan(dateStr);
    });
}

/* ============================================================
   ON MODAL CLOSE → CLEAN ALL TEMPORARY UNSAVED DATA
============================================================ */
document.getElementById("planModal").addEventListener("hidden.bs.modal", () => {

    // 🔥 Only clear UNSAVED temporary data — this prevents losing persisted plans
    tempPlans = {};

    // 🔥 Do NOT modify `savedPlans` here — backend is the truth of persisted plans
    // 🔥 Avoid forcing a full reload; saved operations already kept the UI in sync

    selectedDates = [];
    sliderDates = [];
    currentSlideIndex = 0;
});


