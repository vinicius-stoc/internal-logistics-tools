(function () {
  const searchableSelectIds = [
    "driver_name",
    "route",
    "business_unit",
    "region",
    "frequency",
    "delivery_status",
    "cargo_status",
  ];

  function scheduleSubmit(form) {
    window.clearTimeout(form.dashboardSubmitTimer);

    form.dashboardSubmitTimer = window.setTimeout(function () {
      if (form.dataset.submitted === "true") {
        return;
      }

      if (typeof form.requestSubmit === "function") {
        form.requestSubmit();
        return;
      }

      form.submit();
    }, 350);
  }

  function initializeSearchableSelect(select, form) {
    const placeholder = select.getAttribute("data-placeholder") || "Buscar";
    const isMultiple = select.hasAttribute("multiple");

    if (window.TomSelect) {
      select.dataset.tomSelectInitialized = "true";

      new window.TomSelect(select, {
        allowEmptyOption: true,
        closeAfterSelect: !isMultiple,
        create: false,
        hideSelected: true,
        maxItems: isMultiple ? null : 1,
        maxOptions: 1000,
        placeholder: placeholder,
        plugins: {
          remove_button: {
            title: "Remover selecao",
          },
          clear_button: {
            title: "Limpar selecao",
          },
        },
        render: {
          no_results: function () {
            return '<div class="no-results">Nenhum resultado encontrado</div>';
          },
        },
        onChange: function () {
          scheduleSubmit(form);
        },
      });
      return;
    }

    select.addEventListener("change", function () {
      scheduleSubmit(form);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form[data-auto-submit-filters='true']");

    if (!form) {
      return;
    }

    form.querySelectorAll("input[type='date']").forEach(function (input) {
      input.addEventListener("change", function () {
        scheduleSubmit(form);
      });
    });

    searchableSelectIds.forEach(function (selectId) {
      const select = document.getElementById(selectId);

      if (!select) {
        return;
      }

      initializeSearchableSelect(select, form);
    });

    document.querySelectorAll("[data-clear-filters='true']").forEach(function (link) {
      link.addEventListener("click", function () {
        window.clearTimeout(form.dashboardSubmitTimer);
        form.dataset.submitted = "true";
      });
    });
  });
})();
