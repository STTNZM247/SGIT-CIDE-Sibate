document.addEventListener("DOMContentLoaded", () => {
    const pie = document.querySelector(".page-footnote");

    if (!pie) {
        return;
    }

    pie.insertAdjacentHTML("beforeend", " | Panel activo");
});
