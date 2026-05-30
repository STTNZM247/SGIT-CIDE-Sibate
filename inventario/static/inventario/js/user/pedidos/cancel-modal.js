window.PedidosUsuario = window.PedidosUsuario || {};

window.PedidosUsuario.bindCancelModal = function bindCancelModal() {
  let pendingForm = null;

  const getOverlay = () => document.getElementById('cancelar-confirm-modal');
  const getNumLabel = () => document.getElementById('cancelar-modal-num');

  const openModal = (form, numPedido) => {
    pendingForm = form;
    const label = getNumLabel();
    if (label) label.textContent = `pedido #${numPedido}`;
    const overlay = getOverlay();
    if (overlay) {
      overlay.classList.add('is-open');
      overlay.setAttribute('aria-hidden', 'false');
    }
    document.body.style.overflow = 'hidden';
  };

  const closeModal = () => {
    const overlay = getOverlay();
    if (overlay) {
      overlay.classList.remove('is-open');
      overlay.setAttribute('aria-hidden', 'true');
    }
    document.body.style.overflow = '';
    pendingForm = null;
  };

  document.addEventListener('click', (e) => {
    const triggerBtn = e.target.closest('[data-trigger-cancelar]');
    if (triggerBtn) {
      const form = triggerBtn.closest('[data-cancelar-form]');
      if (form) openModal(form, form.dataset.pedidoNum);
      return;
    }

    if (e.target.closest('#cancelar-modal-back')) {
      closeModal();
      return;
    }

    if (e.target.closest('#cancelar-modal-confirm')) {
      if (pendingForm) pendingForm.submit();
      return;
    }

    const overlay = getOverlay();
    if (overlay && e.target === overlay) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    const overlay = getOverlay();
    if (e.key === 'Escape' && overlay && overlay.classList.contains('is-open')) closeModal();
  });
};
