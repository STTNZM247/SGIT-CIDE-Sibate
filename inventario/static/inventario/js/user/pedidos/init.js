window.PedidosUsuario = window.PedidosUsuario || {};

window.PedidosUsuario.reinit = function reinitPedidosUsuario() {
  if (window.PedidosUsuario.initLightbox) window.PedidosUsuario.initLightbox();
  if (window.PedidosUsuario.initCancelCountdown) window.PedidosUsuario.initCancelCountdown();
  if (window.PedidosUsuario.initDynamicCode) window.PedidosUsuario.initDynamicCode();
};

window.PedidosUsuario.boot = function bootPedidosUsuario() {
  if (window.PedidosUsuario.bindLightboxClose) window.PedidosUsuario.bindLightboxClose();
  if (window.PedidosUsuario.bindCancelModal) window.PedidosUsuario.bindCancelModal();
  window.PedidosUsuario.reinit();
  document.addEventListener('live-section-refreshed', window.PedidosUsuario.reinit);
};
