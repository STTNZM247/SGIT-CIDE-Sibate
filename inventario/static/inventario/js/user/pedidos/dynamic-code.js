window.PedidosUsuario = window.PedidosUsuario || {};

window.PedidosUsuario.initDynamicCode = function initDynamicCode() {
  const parseIsoMs = (v) => {
    if (!v) return NaN;
    const p = Date.parse(v);
    return Number.isFinite(p) ? p : NaN;
  };

  const fmtSecs = (s) => {
    const mm = Math.floor(s / 60);
    return `${mm}:${String(s % 60).padStart(2, '0')}`;
  };

  document.querySelectorAll('[data-devolucion-codigo]:not([data-dev-init])').forEach((box) => {
    box.setAttribute('data-dev-init', '1');

    const ring = box.querySelector('[data-ring]');
    const codeEl = box.querySelector('[data-codigo]');
    const countEl = box.querySelector('[data-countdown]');

    let secs = parseInt(box.dataset.segundos || '0', 10);
    let serverOffsetMs = 0;
    let expiresAtMs = NaN;
    let refreshInFlight = false;

    const syncClock = () => {
      const snMs = parseIsoMs(box.dataset.serverAhora || '');
      if (Number.isFinite(snMs)) serverOffsetMs = snMs - Date.now();
      expiresAtMs = parseIsoMs(box.dataset.expiraEn || '');
      if (Number.isFinite(expiresAtMs)) {
        secs = Math.max(0, Math.ceil((expiresAtMs - (Date.now() + serverOffsetMs)) / 1000));
      }
    };

    const paint = () => {
      const s = Math.max(0, secs);
      if (ring) ring.style.setProperty('--progress', String(Math.max(0, Math.min(1, s / 60))));
      if (countEl) countEl.textContent = fmtSecs(s);
      if (ring) ring.classList.toggle('is-warning', s <= 15);
    };

    const refreshCode = async () => {
      if (refreshInFlight) return;
      refreshInFlight = true;
      try {
        const res = await fetch(`/usuario/pedidos/${box.dataset.pedidoId}/codigo-devolucion/`, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await res.json();
        if (!res.ok || !data.ok) return;
        box.dataset.segundos = String(data.segundos || 0);
        box.dataset.expiraEn = data.expira_en || '';
        box.dataset.serverAhora = data.server_now || '';
        if (codeEl) codeEl.textContent = data.codigo || '------';
        syncClock();
      } catch (_) {
      } finally {
        refreshInFlight = false;
      }
    };

    const tick = async () => {
      if (Number.isFinite(expiresAtMs)) {
        secs = Math.max(0, Math.ceil((expiresAtMs - (Date.now() + serverOffsetMs)) / 1000));
      } else {
        secs = Math.max(0, secs - 1);
      }
      if (secs <= 0) {
        paint();
        await refreshCode();
      }
      paint();
    };

    syncClock();
    paint();
    if (!codeEl || codeEl.textContent.trim() === '------' || secs <= 0 || !Number.isFinite(expiresAtMs)) {
      refreshCode().then(() => paint());
    }
    setInterval(tick, 1000);
  });
};
