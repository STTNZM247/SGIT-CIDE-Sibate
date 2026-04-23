// Custom select para catálogo
document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('customCatalogSelect');
    if (!select) return;

    const selectedBtn = document.getElementById('customSelectSelected');
    const selectedText = document.getElementById('customSelectText');
    const options = document.getElementById('customSelectOptions');
    const input = document.getElementById('categoriaInput');
    const form = select.closest('form');

    function setOpen(open) {
        select.classList.toggle('is-open', open);
        select.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    function closeOptions() {
        setOpen(false);
    }

    selectedBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = select.classList.contains('is-open');
        setOpen(!isOpen);
    });

    options.querySelectorAll('.custom-select__option').forEach(function (opt) {
        opt.addEventListener('click', function () {
            const val = this.getAttribute('data-value') || '';
            input.value = val;
            selectedText.textContent = this.textContent.trim();

            options.querySelectorAll('.custom-select__option').forEach(function (item) {
                item.classList.remove('is-active');
                item.setAttribute('aria-selected', 'false');
            });
            this.classList.add('is-active');
            this.setAttribute('aria-selected', 'true');

            closeOptions();
            if (form) form.submit();
        });
    });

    document.addEventListener('click', function (e) {
        if (!select.contains(e.target)) {
            closeOptions();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeOptions();
        }
    });
});