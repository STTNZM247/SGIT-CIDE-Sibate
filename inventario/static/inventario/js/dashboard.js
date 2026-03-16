document.addEventListener("DOMContentLoaded", () => {
    const pie = document.querySelector(".pie");

    if (!pie) {
        return;
    }

    pie.insertAdjacentHTML("beforeend", " | Panel activo");
});
