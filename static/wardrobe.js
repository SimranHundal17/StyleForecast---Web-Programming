// Current filter state
let CURRENT_FILTER = 'all';

// Render a single card
function cardHTML(item) {
  const btnLabel = (item.status || '').toLowerCase() === 'clean' ? 'Mark as Worn' : 'Mark as Clean';
  return `
    <div class="col-md-4">
      <div class="wardrobe-item-card">
        <div class="wardrobe-item-image">${item.icon || '👕'}</div>
        <div class="wardrobe-item-title">${item.name}</div>
        <div class="wardrobe-item-meta">${item.category} • ${item.status}</div>
        <button class="wardrobe-item-btn" onclick="updateItemStatus(${item.id})">
          ${btnLabel}
        </button>
      </div>
    </div>
  `;
}

// Load items for a given filter and render the grid
async function loadWardrobe(filter = 'all') {
  CURRENT_FILTER = filter;
  const grid = document.getElementById('wardrobe-grid');
  const empty = document.getElementById('empty-state');
  if (!grid) return;

  grid.innerHTML = ''; // clear

  const res = await fetch(`/wardrobe/data?filter=${encodeURIComponent(filter)}`);
  const items = await res.json();

  if (!items || items.length === 0) {
    if (empty) empty.style.display = '';
    return;
  }
  if (empty) empty.style.display = 'none';

  const html = items.map(cardHTML).join('');
  grid.innerHTML = html;
}

// Toggle status and reload with the same filter
async function updateItemStatus(id) {
  await fetch('/wardrobe/update', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ id })
  });
  loadWardrobe(CURRENT_FILTER);
}

// Wire up filter chips
function setupFilters() {
  const chips = document.querySelectorAll('.filter-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      // Active class toggle
      chips.forEach(c => c.classList.remove('filter-active'));
      chip.classList.add('filter-active');

      const f = (chip.dataset.filter || 'all').toLowerCase();
      loadWardrobe(f);
    });
  });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  setupFilters();
  loadWardrobe('all'); // initial load
  // Hook "Add Item" form to use fetch instead of full page reload
  const form = document.getElementById('addItemForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault(); // stop normal form submit

      const formData = new FormData(form);

      // Send form data to Flask route /wardrobe/add-item
      await fetch('/wardrobe/add-item', {
        method: 'POST',
        body: formData
      });

      // Hide modal
      const modalEl = document.getElementById('addItemModal');
      if (modalEl && typeof bootstrap !== 'undefined') {
        const modal =
          bootstrap.Modal.getInstance(modalEl) ||
          new bootstrap.Modal(modalEl);
        modal.hide();
      }

      // Reset form fields
      form.reset();

      // Reload wardrobe with current filter
      loadWardrobe(CURRENT_FILTER);
    });
  }
});

// Expose for inline onclick
window.updateItemStatus = updateItemStatus;
