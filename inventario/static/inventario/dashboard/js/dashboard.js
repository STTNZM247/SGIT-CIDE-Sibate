const initDashboardPage = () => {
    const pie = document.querySelector(".page-footnote");

    if (!pie) {
        // Continua: el dashboard no siempre usa pie de página.
    }

    if (pie && !pie.dataset.dashboardMarked) {
        pie.insertAdjacentHTML("beforeend", " | Panel activo");
        pie.dataset.dashboardMarked = "true";
    }

    const carousel = document.querySelector("[data-market-carousel]");
    if (!carousel) {
        return;
    }

    const track = carousel.querySelector(".market-track");
    if (!track) {
        return;
    }

    let rafId = null;
    let paused = false;
    let offset = 0;
    let loopWidth = 0;

    const stop = () => {
        if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    };

    const measureLoopWidth = (cards, gap) => {
        return cards.reduce((acc, card) => acc + card.getBoundingClientRect().width, 0) + (Math.max(cards.length - 1, 0) * gap);
    };

    const buildInfiniteTrack = () => {
        stop();
        offset = 0;
        track.style.transform = "translate3d(0, 0, 0)";
        track.querySelectorAll(".market-card[data-clone='true']").forEach((node) => node.remove());

        const originalCards = Array.from(track.querySelectorAll(".market-card:not([data-clone='true'])"));
        if (originalCards.length <= 1) {
            return;
        }

        const computedTrack = window.getComputedStyle(track);
        const gap = Number.parseFloat(computedTrack.columnGap || computedTrack.gap || "0") || 0;
        loopWidth = measureLoopWidth(originalCards, gap);

        if (!loopWidth) {
            return;
        }

        const minSets = Math.max(2, Math.ceil((carousel.clientWidth * 2) / loopWidth) + 1);
        for (let setIndex = 1; setIndex < minSets; setIndex += 1) {
            originalCards.forEach((card) => {
                const clone = card.cloneNode(true);
                clone.dataset.clone = "true";
                clone.setAttribute("aria-hidden", "true");

                clone.querySelectorAll("a").forEach((a) => {
                    a.setAttribute("tabindex", "-1");
                    a.setAttribute("aria-hidden", "true");
                });

                track.appendChild(clone);
            });
        }

        const speed = 0.45;
        const animate = () => {
            if (!paused) {
                offset += speed;
                if (offset >= loopWidth) {
                    offset -= loopWidth;
                }
                track.style.transform = `translate3d(${-offset}px, 0, 0)`;
            }
            rafId = requestAnimationFrame(animate);
        };

        rafId = requestAnimationFrame(animate);
    };

    carousel.addEventListener("mouseenter", () => {
        paused = true;
    });

    carousel.addEventListener("mouseleave", () => {
        paused = false;
    });

    let resizeTimer = null;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(buildInfiniteTrack, 160);
    });

    buildInfiniteTrack();
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDashboardPage, { once: true });
} else {
    initDashboardPage();
}
