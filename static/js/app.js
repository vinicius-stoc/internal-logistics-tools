// Global JavaScript hooks for the Django template interface.
(function () {
  function setLoadingState(element) {
    const loadingText = element.getAttribute("data-loading-text");

    if (!loadingText) {
      return;
    }

    element.setAttribute("data-original-text", element.textContent.trim());
    element.textContent = loadingText;
    element.classList.add("disabled");
    element.setAttribute("aria-disabled", "true");
  }

  function clearLoadingState(element) {
    const originalText = element.getAttribute("data-original-text");

    if (!originalText) {
      return;
    }

    element.textContent = originalText;
    element.classList.remove("disabled");
    element.removeAttribute("aria-disabled");
    element.removeAttribute("data-original-text");
  }

  function initializeSidebarToggle() {
    const appShell = document.querySelector(".app-shell");
    const toggle = document.querySelector(".app-sidebar-toggle");

    if (!appShell || !toggle) {
      return;
    }

    const desktopMedia = window.matchMedia("(min-width: 992px)");
    const storageKey = "sidebar-collapsed";
    let collapsed = window.localStorage.getItem(storageKey) === "true";

    function renderSidebarState() {
      const isCollapsed = desktopMedia.matches && collapsed;
      const actionLabel = isCollapsed ? "Expandir menu lateral" : "Recolher menu lateral";

      appShell.classList.toggle("sidebar-collapsed", isCollapsed);
      toggle.setAttribute("aria-expanded", String(!isCollapsed));
      toggle.setAttribute("aria-label", actionLabel);
      toggle.setAttribute("title", actionLabel);
    }

    toggle.addEventListener("click", function () {
      collapsed = !collapsed;
      window.localStorage.setItem(storageKey, String(collapsed));
      renderSidebarState();
    });

    desktopMedia.addEventListener("change", renderSidebarState);
    renderSidebarState();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initializeSidebarToggle();

    document.querySelectorAll("form").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        if (form.hasAttribute("data-confirm-title") && form.dataset.confirmed !== "true") {
          return;
        }

        if (form.dataset.submitted === "true") {
          event.preventDefault();
          return;
        }

        form.dataset.submitted = "true";
        const submitter = event.submitter || form.querySelector("[type='submit']");
        if (submitter) {
          setLoadingState(submitter);
        }
      });
    });

    document.querySelectorAll("a[data-loading-text]").forEach(function (link) {
      link.addEventListener("click", function () {
        setLoadingState(link);
        window.setTimeout(function () {
          clearLoadingState(link);
        }, 3000);
      });
    });
  });
})();
