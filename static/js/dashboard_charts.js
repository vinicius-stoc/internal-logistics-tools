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

  function formatNumber(value) {
    return Number(value || 0).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function formatCurrency(value) {
    return Number(value || 0).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  function formatPercentage(value) {
    return `${formatNumber(value)}%`;
  }

  function buildTooltipLabel(context) {
    const raw = context.raw || {};
    const chartConfig = context.chart.config || {};
    const chartMetadata = (
      chartConfig.metadata ||
      (chartConfig._config && chartConfig._config.metadata) ||
      null
    );
    const metadata = Array.isArray(chartMetadata) ? chartMetadata[context.dataIndex] : null;

    if (raw.driver_name) {
      return [
        raw.driver_name,
        `Registros: ${raw.total_records}`,
        `Entregues: ${raw.delivered_records}`,
        `Atrasados: ${raw.delayed_records || 0}`,
        `Valor NF: ${formatCurrency(raw.total_invoice_value)}`,
        `Severidade atraso: ${formatNumber(raw.delay_severity_hours)}h`,
        `LT operacional médio: ${formatNumber(raw.average_operational_lead_time_hours)}h`,
        `LT transportadora médio: ${formatNumber(raw.average_carrier_lead_time_hours)}h`,
        `Atraso operacional: ${formatPercentage(raw.operational_late_percentage)}`,
        `Atraso transportadora: ${formatPercentage(raw.carrier_late_percentage)}`,
        `Score: ${formatNumber(raw.criticality_score)}`,
      ];
    }

    if (metadata && (metadata.route || metadata.region || metadata.frequency)) {
      const label = metadata.route || metadata.region || metadata.frequency;
      const lines = [label];

      if (metadata.total_records !== undefined) {
        lines.push(`Registros: ${metadata.total_records}`);
      }
      if (metadata.delayed_records !== undefined) {
        lines.push(`Atrasados: ${metadata.delayed_records}`);
      }
      if (metadata.total_invoice_value !== undefined) {
        lines.push(`Valor NF: ${formatCurrency(metadata.total_invoice_value)}`);
      }
      if (metadata.delay_severity_hours !== undefined) {
        lines.push(`Severidade atraso: ${formatNumber(metadata.delay_severity_hours)}h`);
      }
      if (metadata.average_operational_lead_time_hours !== undefined) {
        lines.push(`LT operacional médio: ${formatNumber(metadata.average_operational_lead_time_hours)}h`);
      }
      if (metadata.average_carrier_lead_time_hours !== undefined) {
        lines.push(`LT transportadora médio: ${formatNumber(metadata.average_carrier_lead_time_hours)}h`);
      }
      if (metadata.operational_late_percentage !== undefined) {
        lines.push(`Atraso operacional: ${formatPercentage(metadata.operational_late_percentage)}`);
      }
      if (metadata.carrier_late_percentage !== undefined) {
        lines.push(`Atraso transportadora: ${formatPercentage(metadata.carrier_late_percentage)}`);
      }
      if (metadata.criticality_score !== undefined) {
        lines.push(`Score: ${formatNumber(metadata.criticality_score)}`);
      }
      if (metadata.accumulated_percentage !== undefined) {
        lines.push(`Acumulado: ${formatPercentage(metadata.accumulated_percentage)}`);
      }

      return lines;
    }

    if (metadata && metadata.weekday) {
      return [
        metadata.weekday,
        `${context.dataset.label}: ${formatPercentage(context.parsed.y)}`,
        `Registros: ${metadata.total_records}`,
        `LT operacional médio: ${formatNumber(metadata.average_operational_lead_time_hours)}h`,
        `LT transportadora médio: ${formatNumber(metadata.average_carrier_lead_time_hours)}h`,
      ];
    }

    if (metadata && metadata.issue_date) {
      const parsedValue = context.dataset.yAxisID === "y1" ? context.parsed.y : context.raw;
      const valueLine = context.dataset.yAxisID === "y1"
        ? `${context.dataset.label}: ${formatPercentage(parsedValue)}`
        : `${context.dataset.label}: ${parsedValue}`;

      return [
        metadata.issue_date,
        valueLine,
        `Faturados: ${metadata.total_records}`,
        `Atrasos operacionais: ${metadata.operational_late_records}`,
        `Atrasos transportadora: ${metadata.carrier_late_records}`,
        `Atraso operacional: ${formatPercentage(metadata.operational_late_percentage)}`,
        `Atraso transportadora: ${formatPercentage(metadata.carrier_late_percentage)}`,
      ];
    }

    const parsedValue = context.parsed && context.parsed.y !== undefined ? context.parsed.y : context.raw;
    if (String(context.dataset.label || "").includes("%")) {
      return `${context.dataset.label}: ${formatPercentage(parsedValue)}`;
    }
    return `${context.dataset.label}: ${parsedValue}`;
  }

  function mergeOptions(baseOptions, chartOptions) {
    const merged = Object.assign({}, baseOptions, chartOptions || {});
    merged.plugins = Object.assign({}, baseOptions.plugins || {}, (chartOptions || {}).plugins || {});
    merged.plugins.tooltip = Object.assign(
      {},
      (baseOptions.plugins || {}).tooltip || {},
      (((chartOptions || {}).plugins || {}).tooltip || {})
    );
    merged.plugins.legend = Object.assign(
      {},
      (baseOptions.plugins || {}).legend || {},
      (((chartOptions || {}).plugins || {}).legend || {})
    );
    return merged;
  }

  function buildOptions(chart) {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: chart.type === "doughnut" ? "bottom" : "top",
        },
        tooltip: {
          callbacks: {
            label: buildTooltipLabel,
          },
        },
      },
    };

    return mergeOptions(baseOptions, chart.options || {});
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
      const datasetType = dataset.type || chartConfig.type;
      const color = palette[index % palette.length];

      if (datasetType === "doughnut") {
        return Object.assign(
          {
            backgroundColor: palette,
            borderWidth: 1,
          },
          dataset
        );
      }

      if (datasetType === "line") {
        return Object.assign(
          {
            backgroundColor: color,
            borderColor: color,
            borderWidth: 2,
            fill: false,
            tension: 0.25,
          },
          dataset
        );
      }

      if (datasetType === "bubble") {
        return Object.assign(
          {
            backgroundColor: "rgba(13, 110, 253, 0.35)",
            borderColor: "#0d6efd",
            borderWidth: 1,
          },
          dataset
        );
      }

      return Object.assign(
        {
          backgroundColor: color,
          borderColor: color,
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
      metadata: chart.metadata || null,
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
