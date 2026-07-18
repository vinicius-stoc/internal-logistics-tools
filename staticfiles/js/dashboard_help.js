(function () {
  function readJsonScript(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
      return null;
    }

    try {
      return JSON.parse(element.textContent);
    } catch (error) {
      return null;
    }
  }

  function getByPath(data, path) {
    return String(path || "")
      .split(".")
      .reduce((current, key) => {
        return current && current[key] ? current[key] : null;
      }, data);
  }

  function formatExplanation(explanation) {
    return [
      explanation.summary,
      "",
      "O que esse dado mostra:",
      explanation.calculation,
      "",
      "Como usar na análise:",
      explanation.insight,
      "",
      "Regra de leitura:",
      explanation.formula,
    ].join("\n");
  }

  function showExplanation(explanation) {
    const text = formatExplanation(explanation);

    if (window.Swal && typeof window.Swal.fire === "function") {
      window.Swal.fire({
        title: explanation.title,
        html: text.replaceAll("\n", "<br>"),
        icon: "info",
        confirmButtonText: "Fechar",
      });
      return;
    }

    window.alert(`${explanation.title}\n\n${text}`);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const explanations = readJsonScript("dashboard-explanations-data");

    if (!explanations) {
      return;
    }

    document.querySelectorAll("[data-help-key]").forEach((button) => {
      const explanation = getByPath(explanations, button.getAttribute("data-help-key"));

      if (!explanation) {
        return;
      }

      button.setAttribute("title", explanation.summary);
      button.addEventListener("click", function () {
        showExplanation(explanation);
      });
    });
  });
})();
