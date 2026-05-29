window.PedidosUsuario = window.PedidosUsuario || {};

window.PedidosUsuario.initCancelCountdown = function initCancelCountdown() {
  const fmt = (s) => {
    const mm = Math.floor(s / 60);
    return `${mm}:${String(s % 60).padStart(2, '0')}`;
  };

  document.querySelectorAll('[data-cancelar-pedido]:not([data-cd-init])').forEach((wrap) => {
    wrap.setAttribute('data-cd-init', '1');
    const btn = wrap.querySelector('.pedidos-usuario-btn-cancelar');
    const display = wrap.querySelector('.pedidos-cancelar-countdown');
    if (!display) return;

    let secs = parseInt(wrap.dataset.segundos || '0', 10);
    display.textContent = fmt(secs);

    const timer = setInterval(() => {
      secs -= 1;
      if (secs <= 0) {
        clearInterval(timer);
        display.textContent = '0:00';
        wrap.classList.add('pedidos-cancelar-expirado');
        if (btn) btn.disabled = true;
      } else {
        display.textContent = fmt(secs);
        if (secs <= 60) wrap.classList.add('pedidos-cancelar-urgente');
      }
    }, 1000);

    wrap._cdTimer = timer;
  });
};
