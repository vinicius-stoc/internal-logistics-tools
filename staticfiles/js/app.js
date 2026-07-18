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

  document.addEventListener("DOMContentLoaded", function () {
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
