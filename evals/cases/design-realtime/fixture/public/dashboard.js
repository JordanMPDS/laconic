// Rendered once on load. The "Refresh" button people keep clicking calls this
// same function, which is the behaviour we are trying to remove.
async function load() {
  const res = await fetch('/api/metrics');
  const { rows, computed_at } = await res.json();
  render(rows);
  document.getElementById('stamp').textContent = new Date(computed_at).toLocaleTimeString();
}

document.getElementById('refresh').addEventListener('click', load);
window.addEventListener('load', load);
