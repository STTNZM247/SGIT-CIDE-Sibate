(() => {
  const modal = document.getElementById('modal-catalogo');
  if (!modal) return;

  const stepLabel = document.getElementById('wizard-step-label');
  const pills = Array.from(modal.querySelectorAll('[data-wizard-pill]'));
  const steps = Array.from(modal.querySelectorAll('[data-wizard-step]'));
  const backBtn = document.getElementById('wiz-back');
  const nextBtn = document.getElementById('wiz-next');
  const errBox = document.getElementById('wizard-error-box');
  const okBox = document.getElementById('wizard-ok-box');

  let currentStep = 1;
  let macro = null;
  let categoria = null;
  const endpointMacro = modal.getAttribute('data-url-macro') || '/catalogo/wizard/macro/';
  const endpointCategoria = modal.getAttribute('data-url-categoria') || '/catalogo/wizard/categoria/';
  const endpointSubcategorias = modal.getAttribute('data-url-subcategorias') || '/catalogo/wizard/subcategorias/';
  const endpointCodigo = modal.getAttribute('data-url-codigo') || '/catalogo/wizard/codigo/';
  const codeValidationTimers = new WeakMap();

  const csrfToken = () => {
    const cookie = document.cookie.split('; ').find((x) => x.startsWith('csrftoken='));
    if (cookie) {
      return decodeURIComponent(cookie.split('=')[1]);
    }

    const hiddenInput =
      document.querySelector('#modal-catalogo input[name="csrfmiddlewaretoken"]') ||
      document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (hiddenInput && hiddenInput.value) {
      return hiddenInput.value;
    }

    const metaToken = document.querySelector('meta[name="csrf-token"]');
    return metaToken ? (metaToken.getAttribute('content') || '') : '';
  };

  const showError = (msg) => {
    if (!errBox) return;
    errBox.textContent = msg || 'Error inesperado.';
    errBox.classList.remove('tw-hidden');
  };

  const showOk = (msg) => {
    if (!okBox) return;
    okBox.textContent = msg || '';
    okBox.classList.remove('tw-hidden');
  };

  const clearMessages = () => {
    errBox?.classList.add('tw-hidden');
    okBox?.classList.add('tw-hidden');
  };

  const updateUi = () => {
    steps.forEach((el) => {
      const n = Number(el.getAttribute('data-wizard-step'));
      const isActive = n === currentStep;
      el.classList.toggle('tw-hidden', !isActive);
      el.hidden = !isActive;
    });
    pills.forEach((el) => {
      const n = Number(el.getAttribute('data-wizard-pill'));
      const isActive = n === currentStep;
      el.classList.toggle('is-active', isActive);
      el.classList.toggle('tw-bg-slate-900', isActive);
      el.classList.toggle('tw-text-white', isActive);
      el.classList.toggle('tw-bg-slate-100', !isActive);
      el.classList.toggle('tw-text-slate-600', !isActive);
    });

    backBtn.disabled = currentStep === 1;
    if (currentStep === 1) {
      stepLabel.textContent = 'Paso 1 de 3: crear macro categoría';
      nextBtn.textContent = 'Siguiente';
    } else if (currentStep === 2) {
      stepLabel.textContent = 'Paso 2 de 3: crear categoría';
      nextBtn.textContent = 'Siguiente';
    } else {
      stepLabel.textContent = 'Paso 3 de 3: crear subcategorías';
      nextBtn.textContent = 'Finalizar';
    }

    const activeStep = steps.find((el) => Number(el.getAttribute('data-wizard-step')) === currentStep);
    const firstField = activeStep?.querySelector('input:not([type="hidden"]), select, textarea');
    if (firstField) {
      setTimeout(() => firstField.focus(), 60);
    }
  };

  const safeJson = async (res) => {
    const text = await res.text();
    try {
      return JSON.parse(text || '{}');
    } catch (_e) {
      return {
        ok: false,
        error: `Respuesta no valida del servidor (${res.status}).`,
      };
    }
  };

  const postForm = async (url, data) => {
    const body = new URLSearchParams(data);
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      },
      body,
    });
    const payload = await safeJson(res);
    if (!res.ok && payload.ok !== false) {
      payload.ok = false;
      payload.error = payload.error || `Error HTTP ${res.status}`;
    }
    return payload;
  };

  const postJson = async (url, payload) => {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    const data = await safeJson(res);
    if (!res.ok && data.ok !== false) {
      data.ok = false;
      data.error = data.error || `Error HTTP ${res.status}`;
    }
    return data;
  };

  const normalizeCode = (value) => (value || '').replace(/\D+/g, '');
  const getSubcatCodeInputs = () => Array.from(modal.querySelectorAll('#wiz-subcat-inputs [data-code-field="subcategoria"]'));

  const getUsedSubcatCodes = (excludeInput = null) => {
    const used = new Set();
    getSubcatCodeInputs().forEach((codeInput) => {
      if (!codeInput || codeInput === excludeInput) return;
      const value = normalizeCode(codeInput.value);
      if (value) used.add(value);
    });
    return used;
  };

  const hasLocalDuplicateSubcatCode = (input) => {
    if (!input) return false;
    const current = normalizeCode(input.value);
    if (!current) return false;
    const used = getUsedSubcatCodes(input);
    return used.has(current);
  };

  const findLocalDuplicateSubcats = () => {
    const codeCounts = new Map();

    const rows = Array.from(document.querySelectorAll('#wiz-subcat-inputs tr'));
    rows.forEach((row) => {
      const codigo = normalizeCode(row.querySelector('[data-col="codigo"]')?.value || '');
      const nombre = (row.querySelector('[data-col="nombre"]')?.value || '').trim();
      if (!codigo || !nombre) return;

      codeCounts.set(codigo, (codeCounts.get(codigo) || 0) + 1);
    });

    const duplicatedCodes = Array.from(codeCounts.entries()).filter(([, count]) => count > 1).map(([code]) => code);
    return { duplicatedCodes };
  };

  const setCodeState = (input, statusEl, valid, message) => {
    if (input) {
      input.classList.remove('tw-border-emerald-400', 'tw-ring-1', 'tw-ring-emerald-200', 'tw-border-rose-400', 'tw-ring-rose-200');
      if (valid === true) {
        input.classList.add('tw-border-emerald-400', 'tw-ring-1', 'tw-ring-emerald-200');
      } else if (valid === false) {
        input.classList.add('tw-border-rose-400', 'tw-ring-1', 'tw-ring-rose-200');
      }
    }

    if (statusEl) {
      statusEl.textContent = message || '';
      statusEl.classList.remove('tw-text-emerald-600', 'tw-text-rose-600', 'tw-text-slate-500');
      if (valid === true) {
        statusEl.classList.add('tw-text-emerald-600');
      } else if (valid === false) {
        statusEl.classList.add('tw-text-rose-600');
      } else {
        statusEl.classList.add('tw-text-slate-500');
      }
    }
  };

  const validateCodeRemote = async (nivel, codigo, context = {}) => {
    return postForm(endpointCodigo, {
      modo: 'validar',
      nivel,
      codigo,
      macro_id: context.macro_id || '',
      categoria_id: context.categoria_id || '',
    });
  };

  const generateCodeRemote = async (nivel, context = {}) => {
    return postForm(endpointCodigo, {
      modo: 'generar',
      nivel,
      macro_id: context.macro_id || '',
      categoria_id: context.categoria_id || '',
    });
  };

  const attachCodeValidation = (input, statusEl, nivel, getContext = () => ({})) => {
    if (!input) return;

    const runValidation = async () => {
      const codigo = normalizeCode(input.value);
      input.value = codigo;

      if (!codigo) {
        setCodeState(input, statusEl, null, '');
        return;
      }

      if (nivel === 'subcategoria' && hasLocalDuplicateSubcatCode(input)) {
        setCodeState(input, statusEl, false, 'Código repetido dentro del formulario.');
        return;
      }

      setCodeState(input, statusEl, null, 'Validando...');
      const payload = await validateCodeRemote(nivel, codigo, getContext());
      if (input.value !== codigo) return;

      if (payload.ok && payload.disponible) {
        setCodeState(input, statusEl, true, 'Código disponible.');
      } else {
        const message = payload.error || payload.mensaje || 'Código ya registrado.';
        setCodeState(input, statusEl, false, message);
        showError(message);
      }
    };

    input.addEventListener('input', () => {
      input.value = normalizeCode(input.value);
      clearMessages();
      setCodeState(input, statusEl, null, '');
      const existingTimer = codeValidationTimers.get(input);
      if (existingTimer) {
        clearTimeout(existingTimer);
      }
      const timer = setTimeout(() => {
        runValidation().catch(() => {
          setCodeState(input, statusEl, false, 'No se pudo validar el código.');
        });
      }, 350);
      codeValidationTimers.set(input, timer);
    });

    input.addEventListener('blur', () => {
      input.value = normalizeCode(input.value);
      const existingTimer = codeValidationTimers.get(input);
      if (existingTimer) {
        clearTimeout(existingTimer);
      }
      runValidation().catch(() => {
        setCodeState(input, statusEl, false, 'No se pudo validar el código.');
      });
    });
  };

  const generateCodeForLevel = async (nivel, input, statusEl, getContext = () => ({})) => {
    if (!input) return;
    const button = document.activeElement?.closest?.('[data-code-generate]');
    if (button) {
      button.disabled = true;
      button.classList.add('tw-opacity-70');
    }

    try {
      const payload = await generateCodeRemote(nivel, getContext());
      if (payload.ok && payload.codigo) {
        let generated = payload.codigo;

        if (nivel === 'subcategoria') {
          const usedCodes = getUsedSubcatCodes(input);
          let attempts = 0;
          while (usedCodes.has(generated) && attempts < 12) {
            attempts += 1;
            const retryPayload = await generateCodeRemote(nivel, getContext());
            if (!retryPayload.ok || !retryPayload.codigo) {
              break;
            }
            generated = retryPayload.codigo;
          }

          if (usedCodes.has(generated)) {
            setCodeState(input, statusEl, false, 'No fue posible generar un código único en el formulario.');
            showError('No fue posible generar un código único en el formulario. Intenta nuevamente.');
            return;
          }
        }

        input.value = generated;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        setCodeState(input, statusEl, true, 'Código generado automáticamente.');
      } else {
        setCodeState(input, statusEl, false, payload.error || 'No fue posible generar un código.');
        showError(payload.error || 'No fue posible generar un código.');
      }
    } finally {
      if (button) {
        button.disabled = false;
        button.classList.remove('tw-opacity-70');
      }
    }
  };

  const enforceNumericInput = (input) => {
    if (!input) return;
    input.addEventListener('input', () => {
      input.value = (input.value || '').replace(/\D+/g, '');
    });
  };

  const setMacroSummary = () => {
    const box = document.getElementById('wiz-macro-resumen');
    if (!box || !macro) return;
    box.innerHTML = `
      <p class="tw-text-[11px] tw-font-semibold tw-uppercase tw-tracking-wide tw-text-slate-500">Macro creada</p>
      <p class="tw-mt-1 tw-text-base tw-font-bold tw-text-slate-900">${macro.nombre}</p>
      <p class="tw-mt-1 tw-font-mono tw-text-xs tw-text-slate-500">${macro.codigo}</p>
    `;
  };

  const setCategoriaSummary = () => {
    const box = document.getElementById('wiz-categoria-resumen');
    if (!box || !categoria) return;
    const macroName = macro?.nombre || 'macro';
    box.innerHTML = `
      <p class="tw-text-[11px] tw-font-semibold tw-uppercase tw-tracking-wide tw-text-slate-500">Ruta confirmada</p>
      <p class="tw-mt-1 tw-text-base tw-font-bold tw-text-slate-900">${macroName}/${categoria.nombre}</p>
      <p class="tw-mt-1 tw-font-mono tw-text-xs tw-text-slate-500">${macro?.codigo || ''}/${categoria.codigo}</p>
    `;
  };

  const ensureSubcatRow = () => {
    const tbody = document.getElementById('wiz-subcat-inputs');
    if (!tbody) return;
    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="tw-px-3 tw-py-2 lg:tw-px-4">
        <div class="tw-flex tw-flex-col tw-gap-2">
          <div class="tw-flex tw-items-center tw-gap-2">
            <input class="form-input tw-min-w-[130px] tw-w-full" data-col="codigo" data-code-field="subcategoria" placeholder="Ej: 1110" inputmode="numeric" pattern="[0-9]*" maxlength="20">
            <button type="button" class="tw-inline-flex tw-h-11 tw-w-11 tw-items-center tw-justify-center tw-rounded-xl tw-border tw-border-slate-200 tw-bg-white tw-text-slate-600 hover:tw-bg-slate-50" data-code-generate="subcategoria" title="Generar código automático">
              <svg viewBox="0 0 24 24" aria-hidden="true" class="tw-h-4 tw-w-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 12a9 9 0 1 0 3-6.708" />
                <path d="M3 4v5h5" />
              </svg>
            </button>
          </div>
          <p class="tw-text-[11px] tw-font-medium tw-text-slate-500" data-code-status="subcategoria"></p>
        </div>
      </td>
      <td class="tw-px-3 tw-py-2 lg:tw-px-4"><input class="form-input tw-min-w-[180px] tw-w-full" data-col="nombre" placeholder="Ej: Ajuste y torsion"></td>
      <td class="tw-px-3 tw-py-2 lg:tw-px-4"><input class="form-input tw-min-w-[190px] tw-w-full" data-col="descripcion" placeholder="Opcional"></td>
      <td class="tw-px-3 tw-py-2 lg:tw-px-4">
        <div class="tw-flex tw-items-center tw-justify-start tw-gap-2 tw-whitespace-nowrap">
          <button type="button" class="wiz-row-remove tw-inline-flex tw-h-11 tw-w-11 tw-items-center tw-justify-center tw-rounded-xl tw-border tw-border-slate-300 tw-bg-white tw-text-xl tw-font-bold tw-text-slate-700 hover:tw-bg-slate-50" title="Eliminar fila">-</button>
          <button type="button" class="wiz-row-add tw-inline-flex tw-h-11 tw-w-11 tw-items-center tw-justify-center tw-rounded-xl tw-border tw-border-slate-900 tw-bg-slate-900 tw-text-xl tw-font-bold tw-text-white hover:tw-bg-slate-800" title="Agregar fila">+</button>
        </div>
      </td>
    `;
    row.querySelector('.wiz-row-remove').addEventListener('click', () => {
      row.remove();
      refreshPreview();
    });
    row.querySelector('.wiz-row-add').addEventListener('click', () => {
      ensureSubcatRow();
      refreshPreview();
    });
    const codeInput = row.querySelector('[data-col="codigo"]');
    const codeStatus = row.querySelector('[data-code-status="subcategoria"]');
    enforceNumericInput(codeInput);
    attachCodeValidation(codeInput, codeStatus, 'subcategoria', () => ({
      categoria_id: document.getElementById('wiz-categoria-id')?.value || '',
    }));
    row.querySelectorAll('input').forEach((i) => i.addEventListener('input', refreshPreview));
    tbody.appendChild(row);
  };

  const clearRowInputs = (row) => {
    row.querySelectorAll('input').forEach((input) => {
      input.value = '';
    });
  };

  const collectRows = () => {
    const tbody = document.getElementById('wiz-subcat-inputs');
    if (!tbody) return [];
    return Array.from(tbody.querySelectorAll('tr')).map((tr) => ({
      codigo: (tr.querySelector('[data-col="codigo"]')?.value || '').trim(),
      nombre: (tr.querySelector('[data-col="nombre"]')?.value || '').trim().replace(/\s+/g, ' '),
      descripcion: (tr.querySelector('[data-col="descripcion"]')?.value || '').trim(),
    })).filter((r) => r.codigo && r.nombre);
  };

  const refreshPreview = () => {
    const box = document.getElementById('wiz-subcat-preview');
    if (!box) return;
    const rows = collectRows();
    box.innerHTML = '';
    if (!rows.length) {
      box.innerHTML = '<p class="tw-text-sm tw-text-slate-500">A medida que agregues subcategorías verás aquí la confirmación final de la estructura.</p>';
      return;
    }

    const macroName = macro?.nombre || 'macro';
    const categoriaName = categoria?.nombre || 'categoria';
    rows.forEach((r) => {
      const item = document.createElement('div');
      item.className = 'tw-flex tw-items-start tw-justify-between tw-gap-3 tw-rounded-xl tw-border tw-border-slate-200 tw-bg-white tw-p-3';
      item.innerHTML = `
        <div class="tw-flex tw-items-start tw-gap-3">
          <div class="tw-inline-flex tw-h-10 tw-w-10 tw-items-center tw-justify-center tw-rounded-xl tw-bg-slate-100 tw-text-slate-600">
            <ion-icon name="folder-outline"></ion-icon>
          </div>
          <div>
            <p class="tw-text-sm tw-font-semibold tw-text-slate-900">${macroName}/${categoriaName}/${r.nombre}</p>
            <p class="tw-mt-1 tw-text-xs tw-text-slate-500">${r.descripcion || 'Sin descripción'}</p>
          </div>
        </div>
        <span class="tw-font-mono tw-text-[11px] tw-text-slate-500">${r.codigo}</span>
      `;
      box.appendChild(item);
    });
  };

  const createMacro = async () => {
    const data = {
      codigo_macro: (document.getElementById('wiz-codigo-macro')?.value || '').trim(),
      nombre_catalogo: (document.getElementById('wiz-nombre-macro')?.value || '').trim(),
      descripcion: (document.getElementById('wiz-descripcion-macro')?.value || '').trim(),
      id_ubicacion_fk: (document.getElementById('wiz-ubicacion')?.value || '').trim(),
    };

    if (!data.codigo_macro || !data.nombre_catalogo || !data.id_ubicacion_fk) {
      showError('Completa numero macro, titulo macro y ubicación de bodega.');
      return false;
    }

    const res = await postForm(endpointMacro, data);
    if (!res.ok) {
      showError(res.error || 'No se pudo crear la macro categoría.');
      return false;
    }

    macro = res.macro;
    document.getElementById('wiz-macro-id').value = String(macro.id);
    setMacroSummary();
    showOk(`Macro creada: ${macro.nombre}`);
    return true;
  };

  const createCategoria = async () => {
    const data = {
      macro_id: (document.getElementById('wiz-macro-id')?.value || '').trim(),
      codigo_categoria: (document.getElementById('wiz-codigo-categoria')?.value || '').trim(),
      nombre_categoria: (document.getElementById('wiz-nombre-categoria')?.value || '').trim(),
      descripcion_categoria: (document.getElementById('wiz-descripcion-categoria')?.value || '').trim(),
    };

    if (!data.macro_id || !data.codigo_categoria || !data.nombre_categoria) {
      showError('Completa numero y nombre de categoría.');
      return false;
    }

    const res = await postForm(endpointCategoria, data);
    if (!res.ok) {
      showError(res.error || 'No se pudo crear la categoría.');
      return false;
    }

    categoria = res.categoria;
    document.getElementById('wiz-categoria-id').value = String(categoria.id);
    setCategoriaSummary();
    showOk(`Ruta parcial creada: ${macro?.nombre || ''}/${categoria.nombre}`);
    refreshPreview();
    return true;
  };

  const createSubcategorias = async () => {
    const categoriaId = (document.getElementById('wiz-categoria-id')?.value || '').trim();
    const rows = collectRows();

    if (!categoriaId || rows.length === 0) {
      showError('Agrega al menos una subcategoría válida (codigo y nombre).');
      return false;
    }

    const { duplicatedCodes } = findLocalDuplicateSubcats();
    if (duplicatedCodes.length) {
      showError('Hay códigos repetidos dentro del formulario.');
      return false;
    }

    const res = await postJson(endpointSubcategorias, {
      categoria_id: categoriaId,
      subcategorias: rows,
    });

    if (!res.ok) {
      showError(res.error || 'No se pudieron crear subcategorías.');
      return false;
    }

    showOk(`Proceso completado: ${res.subcategorias.length} subcategoría(s) creadas en ${macro?.nombre || ''}/${categoria?.nombre || ''}.`);
    return true;
  };

  const macroCodeInput = document.getElementById('wiz-codigo-macro');
  const macroCodeStatus = document.getElementById('wiz-codigo-macro-status');
  const categoriaCodeInput = document.getElementById('wiz-codigo-categoria');
  const categoriaCodeStatus = document.getElementById('wiz-codigo-categoria-status');

  attachCodeValidation(macroCodeInput, macroCodeStatus, 'macro');
  attachCodeValidation(categoriaCodeInput, categoriaCodeStatus, 'categoria', () => ({
    macro_id: document.getElementById('wiz-macro-id')?.value || '',
  }));

  const firstSubcatCodeInput = document.querySelector('#wiz-subcat-inputs [data-code-field="subcategoria"]');
  const firstSubcatCodeStatus = document.querySelector('#wiz-subcat-inputs [data-code-status="subcategoria"]');
  attachCodeValidation(firstSubcatCodeInput, firstSubcatCodeStatus, 'subcategoria', () => ({
    categoria_id: document.getElementById('wiz-categoria-id')?.value || '',
  }));

  modal.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-code-generate]');
    if (!button || !modal.contains(button)) return;

    const nivel = (button.getAttribute('data-code-generate') || '').trim();
    if (nivel === 'macro') {
      await generateCodeForLevel('macro', macroCodeInput, macroCodeStatus);
      return;
    }
    if (nivel === 'categoria') {
      await generateCodeForLevel('categoria', categoriaCodeInput, categoriaCodeStatus, () => ({
        macro_id: document.getElementById('wiz-macro-id')?.value || '',
      }));
      return;
    }

    if (nivel === 'subcategoria') {
      const row = button.closest('tr');
      const input = row?.querySelector('[data-code-field="subcategoria"]');
      const status = row?.querySelector('[data-code-status="subcategoria"]');
      await generateCodeForLevel('subcategoria', input, status, () => ({
        categoria_id: document.getElementById('wiz-categoria-id')?.value || '',
      }));
    }
  });

  backBtn?.addEventListener('click', () => {
    clearMessages();
    if (currentStep > 1) currentStep -= 1;
    updateUi();
  });

  nextBtn?.addEventListener('click', async () => {
    clearMessages();
    nextBtn.disabled = true;
    const previousLabel = nextBtn.textContent;
    nextBtn.textContent = currentStep === 3 ? 'Guardando...' : 'Procesando...';
    try {
      if (currentStep === 1) {
        if (await createMacro()) {
          currentStep = 2;
          updateUi();
        }
      } else if (currentStep === 2) {
        if (await createCategoria()) {
          currentStep = 3;
          updateUi();
        }
      } else {
        if (await createSubcategorias()) {
          setTimeout(() => {
            window.location.reload();
          }, 900);
        }
      }
    } catch (err) {
      showError(err?.message || 'No se pudo completar la acción. Revisa tu sesión y conexión.');
    } finally {
      nextBtn.disabled = false;
      nextBtn.textContent = previousLabel;
    }
  });

  document.getElementById('wiz-add-row')?.addEventListener('click', () => {
    ensureSubcatRow();
    refreshPreview();
  });

  document.getElementById('wiz-remove-row')?.addEventListener('click', () => {
    const tbody = document.getElementById('wiz-subcat-inputs');
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    if (rows.length <= 1) {
      clearRowInputs(rows[0]);
    } else {
      rows[0].remove();
    }
    refreshPreview();
  });

  modal.querySelectorAll('input[data-col], textarea[data-col]').forEach((el) => {
    el.addEventListener('input', refreshPreview);
  });

  enforceNumericInput(document.getElementById('wiz-codigo-macro'));
  enforceNumericInput(document.getElementById('wiz-codigo-categoria'));
  modal.querySelectorAll('input[data-col="codigo"]').forEach((el) => enforceNumericInput(el));

  modal.querySelectorAll('[data-modal-close]').forEach((el) => {
    el.addEventListener('click', () => {
      currentStep = 1;
      macro = null;
      categoria = null;
      clearMessages();
      updateUi();
    });
  });

  updateUi();
})();
