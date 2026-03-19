// Custom select para catálogo
document.addEventListener('DOMContentLoaded', function() {
    const select = document.getElementById('customCatalogSelect');
    if (!select) return;
    const selected = document.getElementById('customSelectSelected');
    const options = document.getElementById('customSelectOptions');
    const input = document.getElementById('categoriaInput');
    let isOpen = false;

    function closeOptions() {
        options.style.display = 'none';
        isOpen = false;
    }

    selected.addEventListener('click', function(e) {
        e.stopPropagation();
        isOpen = !isOpen;
        options.style.display = isOpen ? 'block' : 'none';
    });

    const form = select.closest('form');
    options.querySelectorAll('.custom-select__option').forEach(function(opt) {
        opt.addEventListener('click', function(e) {
            input.value = this.getAttribute('data-value');
            selected.childNodes[0].textContent = this.textContent;
            closeOptions();
            if (form) form.submit();
        });
    });

    document.addEventListener('click', function() {
        closeOptions();
    });
});