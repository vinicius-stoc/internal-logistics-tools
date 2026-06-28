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

  function canvasIdFor(chartId) {
    return `chart-${String(chartId).replaceAll("_", "-")}`;
  }

  function hasDatasetData(chart) {
    if (!chart || !chart.data || !Array.isArray(chart.data.datasets)) {
      return false;
    }

    return chart.data.datasets.some((dataset) => {
      return Array.isArray(dataset.data) && dataset.data.length > 0;
    });
  }

  function buildOptions(chart) {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: chart.type === "doughnut" ? "bottom" : "top",
        },
      },
    };

    return Object.assign({}, baseOptions, chart.options || {});
  }

  function applyVisualDefaults(chartConfig) {
    const palette = [
      "#0d6efd",
      "#198754",
      "#ffc107",
      "#dc3545",
      "#6f42c1",
      "#20c997",
      "#fd7e14",
      "#6c757d",
    ];

    chartConfig.data.datasets = chartConfig.data.datasets.map((dataset, index) => {
      if (chartConfig.type === "doughnut") {
        return Object.assign(
          {
            backgroundColor: palette,
            borderWidth: 1,
          },
          dataset
        );
      }

      return Object.assign(
        {
          backgroundColor: palette[index % palette.length],
          borderColor: palette[index % palette.length],
          borderWidth: 1,
        },
        dataset
      );
    });

    return chartConfig;
  }

  function renderChart(chart) {
    const canvas = document.getElementById(canvasIdFor(chart.id));

    if (!canvas || !hasDatasetData(chart)) {
      return;
    }

    const chartConfig = applyVisualDefaults({
      type: chart.type,
      data: chart.data,
      options: buildOptions(chart),
    });

    new Chart(canvas, chartConfig);
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof Chart === "undefined") {
      return;
    }

    const charts = readJsonScript("dashboard-charts-data");

    if (!charts) {
      return;
    }

    Object.keys(charts).forEach((chartKey) => {
      renderChart(charts[chartKey]);
    });
  });
})();
