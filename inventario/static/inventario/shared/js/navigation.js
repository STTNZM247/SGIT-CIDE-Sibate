document.addEventListener("DOMContentLoaded", () => {
    const items = Array.from(document.querySelectorAll(".navigation .list"));
    const navLinks = Array.from(document.querySelectorAll(".navigation .list a"));
    const NAV_ANIMATION_DELAY = 280;

    const syncIndicator = () => {
        const navList = document.querySelector(".navigation ul");
        if (!navList) {
            return;
        }
        const allItems = Array.from(navList.querySelectorAll(".list"));
        const activeIdx = allItems.findIndex((li) => li.classList.contains("active"));
        navList.style.setProperty("--nav-items", String(Math.max(allItems.length, 1)));
        navList.style.setProperty("--active-index", String(activeIdx >= 0 ? activeIdx : 0));
    };

    const setActive = (targetItem) => {
        items.forEach((li) => li.classList.remove("active"));
        if (targetItem) {
            targetItem.classList.add("active");
        }
        syncIndicator();
    };

    const resolveActiveItemByUrl = (url) => {
        const parsed = new URL(url, window.location.origin);
        const path = parsed.pathname;

        // Panel usuario (productos)
        if (path === "/panel_usuario/" || path === "/usuario/inventario/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/panel_usuario/")?.closest(".list") ||
                   navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/usuario/inventario/")?.closest(".list") || null;
        }
        if (path.startsWith("/usuario/producto/")) {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/panel_usuario/")?.closest(".list") || null;
        }
        // Carrito usuario
        if (path === "/usuario/carrito/" || path === "/carrito_usuario/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/usuario/carrito/")?.closest(".list") ||
                   navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/carrito_usuario/")?.closest(".list") || null;
        }
        // Pedidos usuario
        if (path === "/usuario/pedidos/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/usuario/pedidos/")?.closest(".list") || null;
        }
        // Perfil usuario
        if (path === "/perfil/" || path === "/perfil_usuario/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/perfil/")?.closest(".list") ||
                   navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/perfil_usuario/")?.closest(".list") || null;
        }
        // Admin/almacenista paneles
        if (path.startsWith("/catalogo/")) {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/catalogo/")?.closest(".list") || null;
        }
        if (path.startsWith("/producto/")) {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/catalogo/")?.closest(".list") || null;
        }
        if (path === "/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/")?.closest(".list") || null;
        }
        if (path === "/inventario/" || path.startsWith("/inventario/")) {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/inventario/")?.closest(".list") || null;
        }
        if (path === "/usuarios/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/usuarios/")?.closest(".list") || null;
        }
        if (path === "/prestamos/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/prestamos/")?.closest(".list") || null;
        }
        if (path.startsWith("/pedidos/")) {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/pedidos/")?.closest(".list") || null;
        }
        if (path === "/auditorias/") {
            return navLinks.find((link) => new URL(link.href, window.location.origin).pathname === "/auditorias/")?.closest(".list") || null;
        }
        return null;
    };

    const syncPageStyles = (nextDoc) => {
        const currentStyles = Array.from(document.querySelectorAll("link[data-page-style='true']"));
        const nextStyles = Array.from(nextDoc.querySelectorAll("link[data-page-style='true']"));
        const nextHrefs = new Set(nextStyles.map((style) => style.getAttribute("href")));

        currentStyles.forEach((style) => {
            const href = style.getAttribute("href");
            if (!nextHrefs.has(href)) {
                style.remove();
            }
        });

        nextStyles.forEach((style) => {
            const href = style.getAttribute("href");
            const exists = document.querySelector(`link[data-page-style='true'][href='${href}']`);
            if (!exists) {
                const newStyle = document.createElement("link");
                newStyle.rel = "stylesheet";
                newStyle.href = href;
                newStyle.setAttribute("data-page-style", "true");
                document.head.appendChild(newStyle);
            }
        });
    };

    const runPageScripts = async (nextDoc) => {
        const pageScripts = Array.from(nextDoc.querySelectorAll("script[data-page-script='true']"));

        for (const script of pageScripts) {
            if (script.src) {
                await new Promise((resolve, reject) => {
                    const s = document.createElement("script");
                    s.src = script.src;
                    s.async = false;
                    s.onload = resolve;
                    s.onerror = reject;
                    document.body.appendChild(s);
                });
                continue;
            }

            const inlineScript = document.createElement("script");
            inlineScript.textContent = script.textContent;
            document.body.appendChild(inlineScript);
        }
    };

    const navigateWithoutReload = async (url, pushHistory = true) => {
        const response = await fetch(url, {
            method: "GET",
        });

        if (!response.ok || response.redirected) {
            window.location.assign(url);
            return;
        }

        const html = await response.text();
        const nextDoc = new DOMParser().parseFromString(html, "text/html");
        const nextContainer = nextDoc.querySelector(".app-container");
        const currentContainer = document.querySelector(".app-container");

        if (!nextContainer || !currentContainer) {
            window.location.assign(url);
            return;
        }

        syncPageStyles(nextDoc);
        currentContainer.replaceWith(nextContainer.cloneNode(true));
        document.title = nextDoc.title || document.title;
        document.body.classList.remove("modal-open");

        if (pushHistory) {
            history.pushState({ pjax: true }, "", url);
        }

        const activeForUrl = resolveActiveItemByUrl(url);
        setActive(activeForUrl);

        await runPageScripts(nextDoc);
        window.scrollTo({ top: 0, behavior: "auto" });
    };

    setActive(resolveActiveItemByUrl(window.location.href));
    syncIndicator();

    navLinks.forEach((link) => {
        link.addEventListener("click", async (event) => {
            const item = link.closest(".list");
            const href = link.getAttribute("href") || "";
            const targetUrl = new URL(link.href, window.location.origin);

            if (!item) {
                return;
            }

            setActive(item);

            // En enlaces reales, espera la animacion antes de navegar.
            if (!href || href === "#") {
                return;
            }

            const isExternal = targetUrl.origin !== window.location.origin;
            if (isExternal) {
                return;
            }

            const isSamePage = targetUrl.href === window.location.href;
            if (isSamePage) {
                return;
            }

            event.preventDefault();
            window.setTimeout(() => {
                navigateWithoutReload(targetUrl.href).catch(() => {
                    window.location.assign(targetUrl.href);
                });
            }, NAV_ANIMATION_DELAY);
        });
    });

    window.addEventListener("popstate", () => {
        navigateWithoutReload(window.location.href, false).catch(() => {
            window.location.reload();
        });
    });
});
