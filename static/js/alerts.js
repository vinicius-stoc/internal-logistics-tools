(function () {
  function showToast(message, level) {
    if (!message || !window.Swal || typeof window.Swal.fire !== "function") {
      return;
    }

    const iconByLevel = {
      success: "success",
      error: "error",
      danger: "error",
      warning: "warning",
      info: "info",
    };

    window.Swal.fire({
      toast: true,
      position: "top-end",
      icon: iconByLevel[level] || "info",
      title: message,
      showConfirmButton: false,
      timer: 3200,
      timerProgressBar: true,
    });
  }

  function confirmAction(event, element) {
    if (!window.Swal || typeof window.Swal.fire !== "function") {
      return;
    }

    const title = element.getAttribute("data-confirm-title");
    const text = element.getAttribute("data-confirm-text");

    if (!title) {
      return;
    }

    event.preventDefault();

    window.Swal.fire({
      title: title,
      text: text || "",
      icon: element.getAttribute("data-confirm-icon") || "warning",
      showCancelButton: true,
      confirmButtonText: element.getAttribute("data-confirm-button") || "Confirmar",
      cancelButtonText: "Cancelar",
      confirmButtonColor: "#D71920",
    }).then(function (result) {
      if (!result.isConfirmed) {
        return;
      }

      if (element.tagName === "FORM") {
        element.submit();
        return;
      }

      window.location.href = element.href;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-alert-message]").forEach(function (element) {
      showToast(element.getAttribute("data-alert-message"), element.getAttribute("data-alert-level"));
    });

    document.querySelectorAll("[data-feedback-message]").forEach(function (element) {
      element.addEventListener("click", function () {
        showToast(element.getAttribute("data-feedback-message"), element.getAttribute("data-feedback-level") || "info");
      });
    });

    document.querySelectorAll("[data-confirm-title]").forEach(function (element) {
      element.addEventListener(element.tagName === "FORM" ? "submit" : "click", function (event) {
        confirmAction(event, element);
      }, element.tagName === "FORM");
    });
  });
})();
