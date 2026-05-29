// utils.js - Shared utilities

// CSRF cookie resolver
function getCookie(name) {
  let value = null;
  document.cookie.split(';').forEach(c => {
    c = c.trim();
    if (c.startsWith(name + '=')) {
      value = decodeURIComponent(c.slice(name.length + 1));
    }
  });
  return value;
}

// Attach CSRF Token to Axios requests globally
if (typeof axios !== 'undefined') {
  axios.defaults.headers.common['X-CSRFToken'] = getCookie('csrftoken');
}

// Global Bootstrap toast helper
function showBootstrapToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const id = 'toast-' + Date.now();
  const validTypes = ['success', 'danger', 'warning', 'info', 'primary', 'dark'];
  const toastClass = validTypes.includes(type) ? type : 'success';
  
  container.insertAdjacentHTML('beforeend', `
    <div id="${id}" class="toast align-items-center text-bg-${toastClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${toastClass === 'success' ? 'bi-check-circle-fill' : 'bi-info-circle-fill'}"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `);
  
  const toastEl = document.getElementById(id);
  const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
  toast.show();
  
  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}
