document.addEventListener("DOMContentLoaded", () => {

  const planTypeSelect = document.getElementById("planType");
  const calendar = document.getElementById("calendar");
  let selectedDates = [];

  // Toggle plan type
  planTypeSelect.addEventListener("change", () => {
    selectedDates = [];
    renderCalendar();
  });

  // Generate month calendar
  function renderCalendar() {
    calendar.innerHTML = "";
    const today = new Date();
    const month = today.getMonth();
    const year = today.getFullYear();

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Add empty cells for alignment
    for (let i = 0; i < firstDay; i++) {
      const emptyDiv = document.createElement("div");
      calendar.appendChild(emptyDiv);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const div = document.createElement("div");
      div.className = "calendar-day";
      div.textContent = day;
      const dateStr = `${year}-${String(month + 1).padStart(2,"0")}-${String(day).padStart(2,"0")}`;
      div.dataset.date = dateStr;

      div.addEventListener("click", () => {
        if (planTypeSelect.value === "one-day") {
          selectedDates = [dateStr];
          Array.from(calendar.children).forEach(d => d.classList.remove("selected"));
          div.classList.add("selected");
        } else {
          // Trip: select range
          if (selectedDates.length === 0) {
            selectedDates.push(dateStr);
            div.classList.add("selected");
          } else if (selectedDates.length === 1) {
            selectedDates.push(dateStr);
            // Highlight range
            const start = new Date(selectedDates[0]);
            const end = new Date(selectedDates[1]);
            Array.from(calendar.children).forEach(d => {
              const dDate = new Date(d.dataset.date);
              if (!isNaN(dDate) && dDate >= start && dDate <= end) d.classList.add("selected");
            });
          } else {
            selectedDates = [dateStr];
            Array.from(calendar.children).forEach(d => d.classList.remove("selected"));
            div.classList.add("selected");
          }
        }
      });

      calendar.appendChild(div);
    }
  }

  renderCalendar();

  // Submit form
  const planForm = document.getElementById("planForm");
  planForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!selectedDates.length) return alert("Please select date(s)");

    const location = locationInput.value;
    const occasion = document.getElementById("occasion").value;
    const weather = document.getElementById("weather").value;
    const type = planTypeSelect.value;

    let data = { type, location, occasion, weather };
    if (type === "one-day") data.date = selectedDates[0];
    else data.start_date = selectedDates[0], data.end_date = selectedDates[1] || selectedDates[0];

    const res = await fetch("/api/plans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      alert("Plan added and outfit generated!");
      selectedDates = [];
      renderCalendar();
      planForm.reset();
    } else {
      alert("Error adding plan");
    }
  });
});
