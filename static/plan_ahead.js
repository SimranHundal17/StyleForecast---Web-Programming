// static/plan_ahead.js
// Plan Ahead JS — supports single & multi day with slider modal

const planType = document.getElementById("planType");
const yearSelect = document.getElementById("yearSelect");
const monthSelect = document.getElementById("monthSelect");
const calendar = document.getElementById("calendar");

const planModal = new bootstrap.Modal(document.getElementById("planModal"));
const modalDateRange = document.getElementById("modalDateRange");

const locationInput = document.getElementById("locationInput");
const suggestionsBox = document.getElementById("locationSuggestions");
const occasionInput = document.getElementById("occasionInput");
const weatherInput = document.getElementById("weatherInput");
const savePlanBtn = document.getElementById("savePlanBtn");

const outfitPreview = document.getElementById("outfitPreview");
const feedbackButtons = document.getElementById("feedbackButtons");
const ratingBox = document.getElementById("ratingBox");
const saveMessage = document.getElementById("saveMessage");

const likeBtn = document.getElementById("likeBtn");
const dislikeBtn = document.getElementById("dislikeBtn");
const deleteBtn = document.getElementById("deleteBtn");
const skipRatingBtn = document.getElementById("skipRatingBtn");

let selectedLat = null;
let selectedLon = null;
let lastGenerated = null;
let selectedDates = []; // for multi-select
let currentSlideIndex = 0;
let savedPlans = {}; // map by date string
let autocompleteTimeout = null;

const today = new Date();

// Fill year/month
for (let y = today.getFullYear(); y <= today.getFullYear() + 2; y++) {
  const opt = document.createElement("option");
  opt.value = y;
  opt.textContent = y;
  if (y === today.getFullYear()) opt.selected = true;
  yearSelect.appendChild(opt);
}
const months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
months.forEach((m, i) => {
  const opt = document.createElement("option");
  opt.value = i;
  opt.textContent = m;
  if (i === today.getMonth()) opt.selected = true;
  monthSelect.appendChild(opt);
});

// AUTOCOMPLETE
locationInput.addEventListener("input", () => {
  const q = locationInput.value.trim();
  suggestionsBox.innerHTML = "";
  selectedLat = null; selectedLon = null;
  savePlanBtn.disabled = true;
  clearTimeout(autocompleteTimeout);
  if (!q) { suggestionsBox.style.display='none'; return; }

  autocompleteTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`/api/location/autocomplete?q=${encodeURIComponent(q)}`, { credentials: "include" });
      const results = await res.json();
      suggestionsBox.innerHTML = "";
      suggestionsBox.style.display = "block";
      if (!results.length) {
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
          suggestionsBox.style.display='none';
          savePlanBtn.disabled = false;
        });
        suggestionsBox.appendChild(div);
      });
    } catch (err) {
      console.error(err);
    }
  }, 250);
});

document.addEventListener("click", e => {
  if (!locationInput.contains(e.target)) {
    suggestionsBox.innerHTML = ""; suggestionsBox.style.display='none';
  }
});

// Auto-detect on page load
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(async pos => {
    try {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      const url = `/api/location/reverse?lat=${lat}&lon=${lon}`;
      const res = await fetch(url, { credentials: "include" });
      const data = await res.json();
      if (!data.error) {
        locationInput.value = data.label;
        selectedLat = data.lat; selectedLon = data.lon;
        savePlanBtn.disabled = false;
      }
    } catch (err) { /* ignore */ }
  }, () => {});
}

// Calendar generation
function generateCalendar() {
  calendar.innerHTML = "";
  const year = parseInt(yearSelect.value);
  const month = parseInt(monthSelect.value);
  const firstDay = new Date(year, month, 1).getDay();
  const lastDate = new Date(year, month + 1, 0).getDate();

  for (let i = 0; i < firstDay; i++) calendar.appendChild(document.createElement("div"));

  for (let d = 1; d <= lastDate; d++) {
    const div = document.createElement("div");
    div.className = "calendar-day";
    const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    div.textContent = d;

    if (new Date(dateStr) < new Date(today.toDateString())) div.classList.add("disabled");
    if (savedPlans[dateStr]) div.classList.add("selected");

    div.addEventListener("click", () => {
      if (new Date(dateStr) < new Date(today.toDateString())) return;
      onCalendarClick(dateStr, div);
    });

    calendar.appendChild(div);
  }
}
yearSelect.addEventListener("change", generateCalendar);
monthSelect.addEventListener("change", generateCalendar);
generateCalendar();

// handle calendar clicks for one/multi
function onCalendarClick(dateStr, dayEl) {
  if (planType.value === "one") {
    selectedDates = [dateStr];
    openModalForDates(selectedDates);
  } else {
    if (!selectedDates.length) {
      selectedDates = [dateStr];
      dayEl.classList.add("range");
    } else if (selectedDates.length === 1) {
      selectedDates.push(dateStr);
      selectedDates.sort();
      // expand all dates in range
      const start = new Date(selectedDates[0]);
      const end = new Date(selectedDates[1]);
      selectedDates = [];
      for(let d=start; d<=end; d.setDate(d.getDate()+1)){
        const ds = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
        selectedDates.push(ds);
      }
      openModalForDates(selectedDates);
      document.querySelectorAll('.calendar-day.range').forEach(n => n.classList.remove('range'));
    } else {
      selectedDates = [dateStr];
    }
  }
}

// modal logic
function openModalForDates(dates) {
  currentSlideIndex = 0;
  modalDateRange.textContent = dates.length === 1 ? dates[0] : `${dates[0]} → ${dates[dates.length-1]}`;
  planModal.show();

  const first = dates[0];
  if (savedPlans[first]) {
    loadPlanIntoModal(savedPlans[first]);
  } else {
    outfitPreview.innerHTML = "";
    feedbackButtons.style.display = "none";
    ratingBox.classList.add("d-none");
    saveMessage.classList.add("d-none");
    locationInput.value = "";
    weatherInput.value = "";
    occasionInput.value = "Casual";
    selectedLat = null; selectedLon = null;
    savePlanBtn.disabled = true;
  }
}

// load a saved plan into modal UI
function loadPlanIntoModal(plan) {
  locationInput.value = plan.location || "";
  occasionInput.value = plan.occasion || "Casual";
  weatherInput.value = plan.weather || "";
  selectedLat = plan.lat; selectedLon = plan.lon;
  outfitPreview.innerHTML = "";
  if (plan.outfit && plan.outfit.length) {
    plan.outfit.forEach(it => {
      const d = document.createElement("div"); d.className = "outfit-item"; d.textContent = it; outfitPreview.appendChild(d);
    });
    feedbackButtons.style.display = "block";
  } else {
    feedbackButtons.style.display = "none";
  }
  savePlanBtn.disabled = false;
}

// generate outfit (fetch weather if auto-detect)
savePlanBtn.addEventListener("click", async () => {
  if (!selectedDates.length) return;
  if (!selectedLat || !selectedLon) {
    alert("Please select a valid location (click suggestion).");
    return;
  }

  outfitPreview.innerHTML = "";
  feedbackButtons.style.display = "none";
  ratingBox.classList.add("d-none");
  saveMessage.classList.add("d-none");

  // check weather selection
  let weatherToUse = weatherInput.value.trim();
  const autoDetect = weatherToUse.toLowerCase() === "auto-detect";

  try {
    if (autoDetect) {
      // fetch weather for each date
      for (let i = 0; i < selectedDates.length; i++) {
        const date = selectedDates[i];
        const res = await fetch(`/api/weather_for_date?lat=${selectedLat}&lon=${selectedLon}&date=${date}`);
        const data = await res.json();
        if (data.error) {
          alert(`Weather not available for ${date}. Please select manually.`);
          return; // stop outfit generation
        }
        // populate weather for each date
        savedPlans[date] = savedPlans[date] || {};
        savedPlans[date].weather = data.weather;
      }
      weatherToUse = ""; // optional: outfit API can use per-day weather
    } else {
      // user selected manually, apply to all selected dates
      selectedDates.forEach(date => {
        savedPlans[date] = savedPlans[date] || {};
        savedPlans[date].weather = weatherToUse;
      });
    }

    // now generate outfit per date
    for (let i = 0; i < selectedDates.length; i++) {
      const date = selectedDates[i];
      const planData = savedPlans[date];

      const res = await fetch("/api/get_outfit", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: selectedLat,
          lon: selectedLon,
          occasion: occasionInput.value,
          weather: planData.weather
        })
      });
      const data = await res.json();
      if (data.error) {
        outfitPreview.innerHTML = `<div class="text-danger text-center">${data.error}</div>`;
        return;
      }

      // show outfit preview
      planData.outfit = data.outfit;
      outfitPreview.innerHTML = ""; // clear for first slide
      data.outfit.forEach(it => {
        const d = document.createElement("div");
        d.className = "outfit-item";
        d.textContent = it;
        outfitPreview.appendChild(d);
      });
      feedbackButtons.style.display = "block";
      lastGenerated = planData;
    }

  } catch (err) {
    console.error(err);
    outfitPreview.innerHTML = `<div class="text-danger text-center">Unable to generate outfit</div>`;
  }
});

// existing logic for like, dislike, delete, rating, skipRating remains unchanged
// ...

// When modal closes, persist highlights
document.getElementById('planModal').addEventListener('hidden.bs.modal', () => {
  generateCalendar();
  selectedDates = [];
});

generateCalendar();
