window.PedidosUsuario = window.PedidosUsuario || {};

window.PedidosUsuario.initLightbox = function initLightbox() {
  const lightbox = document.getElementById('pedidosUsuarioLightbox');
  const lightboxImg = document.getElementById('pedidosUsuarioLightboxImg');
  if (!lightbox || !lightboxImg) return;

  document.querySelectorAll('.pedidos-usuario-evidencia-item[data-evidencia-src]:not([data-ev-init])').forEach((item) => {
    item.setAttribute('data-ev-init', '1');
    item.addEventListener('click', () => {
      lightboxImg.src = item.dataset.evidenciaSrc;
      lightboxImg.alt = item.dataset.evidenciaAlt || 'Evidencia';
      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.classList.add('modal-open');
    });
  });
};

window.PedidosUsuario.bindLightboxClose = function bindLightboxClose() {
  const close = () => {
    const lb = document.getElementById('pedidosUsuarioLightbox');
    const img = document.getElementById('pedidosUsuarioLightboxImg');
    if (lb) {
      lb.classList.remove('is-open');
      lb.setAttribute('aria-hidden', 'true');
    }
    if (img) img.src = '';
    document.body.classList.remove('modal-open');
  };

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-close-evidencia]');
    if (btn) close();
    const lb = document.getElementById('pedidosUsuarioLightbox');
    if (lb && e.target === lb) close();
  });

  document.addEventListener('keydown', (e) => {
    const lb = document.getElementById('pedidosUsuarioLightbox');
    if (e.key === 'Escape' && lb && lb.classList.contains('is-open')) close();
  });
};
