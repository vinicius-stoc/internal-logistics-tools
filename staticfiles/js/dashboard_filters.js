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

  function initializeSearchableSelect(select) {
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
            title: "Remover seleção",
          },
          clear_button: {
            title: "Limpar seleção",
          },
        },
        render: {
          no_results: function () {
            return '<div class="no-results">Nenhum resultado encontrado</div>';
          },
        },
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    searchableSelectIds.forEach(function (selectId) {
      const select = document.getElementById(selectId);

      if (!select) {
        return;
      }

      initializeSearchableSelect(select);
    });
  });
})();
