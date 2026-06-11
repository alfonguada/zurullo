// ── ZURULLO WORLD CUP — app.js ──

function showFlash(msg, type) {
  const container = document.querySelector('.flash-container') || createFlashContainer();
  const div = document.createElement('div');
  div.className = `flash flash-${type}`;
  div.innerHTML = `${msg} <button onclick="this.parentElement.remove()">×</button>`;
  container.appendChild(div);
  setTimeout(() => div.remove(), 4000);
}

function createFlashContainer() {
  const c = document.createElement('div');
  c.className = 'flash-container';
  document.body.appendChild(c);
  return c;
}

// Auto-dismiss flashes after 5s
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => el.remove(), 5000);
  });

  // Score inputs: prevent negative, max 30
  document.querySelectorAll('.score-inp').forEach(inp => {
    inp.addEventListener('change', () => {
      let v = parseInt(inp.value);
      if (isNaN(v) || v < 0) inp.value = 0;
      if (v > 30) inp.value = 30;
    });
  });
});
