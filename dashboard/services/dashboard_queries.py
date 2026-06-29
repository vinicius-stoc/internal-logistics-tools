from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Optional

from django.db.models import Avg, Count, Q, Sum

from imports.models import ImportBatch, LeadTimeRecord
from imports.services.lead_time_calculation_service import (
    CARRIER_TARGET_HOURS,
    OPERATIONAL_TARGET_HOURS,
)

from .analytics_explanations import get_analytics_explanations
from .chart_contracts import make_chart_contract, make_single_dataset_chart
from .dashboard_filters import DashboardFilters


DELIVERED_STATUS_LOOKUP = Q(delivery_status__icontains="entreg")
DELAYED_RECORDS_LOOKUP = Q(is_operational_late=True) | Q(is_carrier_late=True)
TOP_GROUP_LIMIT = 10


def get_dashboard_context(filters: Optional[DashboardFilters] = None):
    filters = filters or DashboardFilters()
    base_queryset = LeadTimeRecord.objects.select_related("import_batch")
    filtered_queryset = filters.apply_to_queryset(base_queryset)

    criticality_totals = _get_criticality_totals(filtered_queryset)
    driver_rows = _get_group_criticality_rows(
        filtered_queryset,
        group_field="driver_name",
        empty_label="Sem motorista",
        totals=criticality_totals,
    )
    route_rows = _get_group_criticality_rows(
        filtered_queryset,
        group_field="route",
        empty_label="Sem pauta",
        totals=criticality_totals,
    )
    city_rows = _get_group_criticality_rows(
        filtered_queryset,
        group_field="city",
        empty_label="Sem cidade",
        totals=criticality_totals,
    )
    region_rows = _get_group_criticality_rows(
        filtered_queryset,
        group_field="region",
        empty_label="Sem regiao",
        totals=criticality_totals,
        include_empty_groups=False,
    )
    frequency_rows = _get_group_criticality_rows(
        filtered_queryset,
        group_field="frequency",
        empty_label="Sem frequencia",
        totals=criticality_totals,
        include_empty_groups=False,
    )
    cards = _get_cards(filtered_queryset, route_rows)

    return {
        "filters": filters.as_dict(),
        "filter_errors": filters.errors,
        "filter_options": _get_filter_options(),
        "cards": cards,
        "charts": {
            "records_by_day": _get_records_by_day_chart(filtered_queryset),
            "driver_efficiency_scatter": _get_driver_efficiency_scatter_chart(driver_rows),
            "critical_routes_ranking": _get_critical_routes_ranking_chart(route_rows),
            "weekday_bottleneck": _get_weekday_bottleneck_chart(filtered_queryset),
            "delay_pareto": _get_delay_pareto_chart(filtered_queryset),
            "lead_time_distribution": _get_lead_time_distribution_chart(filtered_queryset),
            "region_lead_time_comparison": _get_dimension_lead_time_comparison_chart(
                region_rows,
                chart_id="region_lead_time_comparison",
                title="Lead time por regiao",
                metadata_key="region",
            ),
            "frequency_lead_time_comparison": _get_dimension_lead_time_comparison_chart(
                frequency_rows,
                chart_id="frequency_lead_time_comparison",
                title="Lead time por frequencia",
                metadata_key="frequency",
            ),
        },
        "tables": {
            "driver_outliers": _get_driver_outliers_table(filtered_queryset, driver_rows),
            "critical_routes": _get_critical_routes_table(filtered_queryset, route_rows),
            "critical_cities": _get_critical_cities_table(city_rows),
            "critical_regions": _get_critical_dimension_table(region_rows, "region"),
            "critical_frequencies": _get_critical_dimension_table(frequency_rows, "frequency"),
            "invoice_outliers": _get_invoice_outliers_table(filtered_queryset),
            "status_inconsistencies": _get_status_inconsistencies_table(filtered_queryset),
        },
        "explanations": get_analytics_explanations(),
        "metadata": {
            "last_successful_import": _get_last_successful_import(),
            "has_data": cards["total_records"] > 0,
            "operational_target_hours": _format_decimal(OPERATIONAL_TARGET_HOURS),
            "carrier_target_hours": _format_decimal(CARRIER_TARGET_HOURS),
        },
    }


def _get_cards(queryset, route_rows):
    status_inconsistency_filter = _get_status_inconsistency_filter()
    aggregates = queryset.aggregate(
        total_records=Count("id"),
        delivered_records=Count("id", filter=DELIVERED_STATUS_LOOKUP),
        total_invoice_value=Sum("invoice_value"),
        delayed_invoice_value=Sum("invoice_value", filter=DELAYED_RECORDS_LOOKUP),
        average_operational_lead_time_hours=Avg("operational_lead_time_hours"),
        average_carrier_lead_time_hours=Avg("carrier_lead_time_hours"),
        operational_late_records=Count("id", filter=Q(is_operational_late=True)),
        carrier_late_records=Count("id", filter=Q(is_carrier_late=True)),
        status_inconsistency_count=Count("id", filter=status_inconsistency_filter),
    )

    total_records = aggregates["total_records"] or 0
    delivered_records = aggregates["delivered_records"] or 0
    operational_late_records = aggregates["operational_late_records"] or 0
    carrier_late_records = aggregates["carrier_late_records"] or 0
    status_inconsistency_count = aggregates["status_inconsistency_count"] or 0
    top_critical_route = route_rows[0] if route_rows else None

    return {
        "total_records": total_records,
        "delivered_records": delivered_records,
        "pending_records": total_records - delivered_records,
        "total_invoice_value": _format_decimal(aggregates["total_invoice_value"]),
        "average_operational_lead_time_hours": _format_decimal(
            aggregates["average_operational_lead_time_hours"]
        ),
        "average_carrier_lead_time_hours": _format_decimal(
            aggregates["average_carrier_lead_time_hours"]
        ),
        "operational_late_records": operational_late_records,
        "carrier_late_records": carrier_late_records,
        "operational_late_percentage": _format_percentage(operational_late_records, total_records),
        "carrier_late_percentage": _format_percentage(carrier_late_records, total_records),
        "operational_sla_rate": _format_percentage(
            total_records - operational_late_records,
            total_records,
        ),
        "carrier_sla_rate": _format_percentage(
            total_records - carrier_late_records,
            total_records,
        ),
        "operational_target_hours": _format_decimal(OPERATIONAL_TARGET_HOURS),
        "carrier_target_hours": _format_decimal(CARRIER_TARGET_HOURS),
        "operational_lead_time_p90_hours": _format_decimal(
            _get_percentile(
                queryset.exclude(operational_lead_time_hours__isnull=True)
                .order_by("operational_lead_time_hours")
                .values_list("operational_lead_time_hours", flat=True),
                90,
            )
        ),
        "carrier_lead_time_p90_hours": _format_decimal(
            _get_percentile(
                queryset.exclude(carrier_lead_time_hours__isnull=True)
                .order_by("carrier_lead_time_hours")
                .values_list("carrier_lead_time_hours", flat=True),
                90,
            )
        ),
        "delayed_invoice_value": _format_decimal(aggregates["delayed_invoice_value"]),
        "top_critical_route": _format_critical_route_card(top_critical_route),
        "status_inconsistency_count": status_inconsistency_count,
        "status_inconsistency_percentage": _format_percentage(
            status_inconsistency_count,
            total_records,
        ),
    }


def _get_filter_options():
    return {
        "drivers": _get_distinct_values("driver_name"),
        "routes": _get_distinct_values("route"),
        "business_units": _get_distinct_values("business_unit"),
        "regions": _get_distinct_values("region"),
        "frequencies": _get_distinct_values("frequency"),
        "delivery_statuses": _get_distinct_values("delivery_status"),
        "cargo_statuses": _get_distinct_values("cargo_status"),
    }


def _get_distinct_values(field_name):
    return list(
        LeadTimeRecord.objects.exclude(**{field_name: ""})
        .order_by(field_name)
        .values_list(field_name, flat=True)
        .distinct()
    )


def _get_records_by_day_chart(queryset):
    rows = (
        queryset.values("invoice_issue_date")
        .annotate(total=Count("id"))
        .order_by("invoice_issue_date")
    )

    return make_single_dataset_chart(
        chart_id="records_by_day",
        title="Registros por dia",
        chart_type="bar",
        labels=[_format_date(row["invoice_issue_date"]) for row in rows],
        label="Registros",
        data=[row["total"] for row in rows],
    )


def _get_driver_efficiency_scatter_chart(driver_rows):
    rows = sorted(
        driver_rows,
        key=lambda row: (-row["total_records"], row["label"]),
    )[:TOP_GROUP_LIMIT]
    max_invoice_value = max([row["total_invoice_value_raw"] for row in rows], default=Decimal("0"))

    data_points = []
    for row in rows:
        point = {
            "x": row["total_records"],
            "y": _to_float(row["average_operational_lead_time_hours_raw"]),
            "r": _get_bubble_radius(row["total_invoice_value_raw"], max_invoice_value),
            "driver_name": row["label"],
            "total_records": row["total_records"],
            "delivered_records": row["delivered_records"],
            "delayed_records": row["delayed_records"],
            "total_invoice_value": _to_float(row["total_invoice_value_raw"]),
            "delay_severity_hours": _to_float(row["delay_severity_hours_raw"]),
            "average_operational_lead_time_hours": _to_float(
                row["average_operational_lead_time_hours_raw"]
            ),
            "average_carrier_lead_time_hours": _to_float(row["average_carrier_lead_time_hours_raw"]),
            "operational_late_percentage": _to_float(row["operational_late_percentage_raw"]),
            "carrier_late_percentage": _to_float(row["carrier_late_percentage_raw"]),
            "criticality_score": _to_float(row["criticality_score_raw"]),
        }
        data_points.append(point)

    return make_chart_contract(
        chart_id="driver_efficiency_scatter",
        title="Eficiencia por motorista: volume x lead time",
        chart_type="bubble",
        labels=[row["label"] for row in rows],
        datasets=[
            {
                "label": "Motoristas",
                "data": data_points,
            }
        ],
        options={
            "scales": {
                "x": {
                    "title": {
                        "display": True,
                        "text": "Registros",
                    },
                    "beginAtZero": True,
                },
                "y": {
                    "title": {
                        "display": True,
                        "text": "Lead time operacional medio (h)",
                    },
                    "beginAtZero": True,
                },
            }
        },
        metadata={"pointType": "driver_efficiency"},
    )


def _get_critical_routes_ranking_chart(route_rows):
    rows = route_rows[:TOP_GROUP_LIMIT]
    metadata = [_format_group_metadata(row, "route") for row in rows]

    return make_single_dataset_chart(
        chart_id="critical_routes_ranking",
        title="Rotas criticas",
        chart_type="bar",
        labels=[row["label"] for row in rows],
        label="Score",
        data=[_to_float(row["criticality_score_raw"]) for row in rows],
        options={
            "indexAxis": "y",
            "scales": {
                "x": {
                    "beginAtZero": True,
                    "max": 100,
                }
            },
        },
        metadata=metadata,
    )


def _get_weekday_bottleneck_chart(queryset):
    weekdays = [
        "Segunda",
        "Terca",
        "Quarta",
        "Quinta",
        "Sexta",
        "Sabado",
        "Domingo",
    ]
    grouped_rows = {
        index: {
            "total_records": 0,
            "operational_late_records": 0,
            "carrier_late_records": 0,
            "operational_lead_time_sum": Decimal("0"),
            "carrier_lead_time_sum": Decimal("0"),
            "operational_lead_time_count": 0,
            "carrier_lead_time_count": 0,
        }
        for index in range(7)
    }

    rows = queryset.exclude(invoice_issue_date__isnull=True).values_list(
        "invoice_issue_date",
        "is_operational_late",
        "is_carrier_late",
        "operational_lead_time_hours",
        "carrier_lead_time_hours",
    )
    for issue_date, is_operational_late, is_carrier_late, operational_hours, carrier_hours in rows:
        weekday = issue_date.weekday()
        grouped_row = grouped_rows[weekday]
        grouped_row["total_records"] += 1
        grouped_row["operational_late_records"] += 1 if is_operational_late else 0
        grouped_row["carrier_late_records"] += 1 if is_carrier_late else 0
        if operational_hours is not None:
            grouped_row["operational_lead_time_sum"] += Decimal(operational_hours)
            grouped_row["operational_lead_time_count"] += 1
        if carrier_hours is not None:
            grouped_row["carrier_lead_time_sum"] += Decimal(carrier_hours)
            grouped_row["carrier_lead_time_count"] += 1

    metadata = []
    operational_data = []
    carrier_data = []
    for index in range(7):
        row = grouped_rows[index]
        operational_data.append(_to_float(_safe_divide(row["operational_late_records"] * 100, row["total_records"])))
        carrier_data.append(_to_float(_safe_divide(row["carrier_late_records"] * 100, row["total_records"])))
        metadata.append(
            {
                "weekday": weekdays[index],
                "total_records": row["total_records"],
                "average_operational_lead_time_hours": _format_decimal(
                    _safe_divide(
                        row["operational_lead_time_sum"],
                        row["operational_lead_time_count"],
                    )
                ),
                "average_carrier_lead_time_hours": _format_decimal(
                    _safe_divide(
                        row["carrier_lead_time_sum"],
                        row["carrier_lead_time_count"],
                    )
                ),
            }
        )

    return make_chart_contract(
        chart_id="weekday_bottleneck",
        title="Gargalo por dia da semana",
        chart_type="bar",
        labels=weekdays,
        datasets=[
            {
                "label": "Atraso operacional %",
                "data": operational_data,
            },
            {
                "label": "Atraso transportadora %",
                "data": carrier_data,
            },
        ],
        options={
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "max": 100,
                }
            }
        },
        metadata=metadata,
    )


def _get_delay_pareto_chart(queryset):
    delayed_queryset = queryset.filter(DELAYED_RECORDS_LOOKUP)
    rows = list(
        delayed_queryset.values("route")
        .annotate(delayed_records=Count("id"))
        .order_by("-delayed_records", "route")[:15]
    )
    total_delayed_records = delayed_queryset.count()
    accumulated_records = 0
    labels = []
    bar_data = []
    line_data = []
    metadata = []

    for row in rows:
        delayed_records = row["delayed_records"]
        accumulated_records += delayed_records
        accumulated_percentage = _safe_divide(accumulated_records * 100, total_delayed_records)
        route = row["route"] or "Sem pauta"

        labels.append(route)
        bar_data.append(delayed_records)
        line_data.append(_to_float(accumulated_percentage))
        metadata.append(
            {
                "route": route,
                "delayed_records": delayed_records,
                "accumulated_percentage": _format_decimal(accumulated_percentage),
            }
        )

    return make_chart_contract(
        chart_id="delay_pareto",
        title="Pareto de atrasos por rota",
        chart_type="bar",
        labels=labels,
        datasets=[
            {
                "label": "Atrasos",
                "data": bar_data,
                "type": "bar",
                "yAxisID": "y",
            },
            {
                "label": "Acumulado %",
                "data": line_data,
                "type": "line",
                "yAxisID": "y1",
            },
        ],
        options={
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "position": "left",
                },
                "y1": {
                    "beginAtZero": True,
                    "max": 100,
                    "position": "right",
                    "grid": {
                        "drawOnChartArea": False,
                    },
                },
            }
        },
        metadata=metadata,
    )


def _get_lead_time_distribution_chart(queryset):
    bucket_labels = ["0-24h", "24-48h", "48-72h", "72-96h", ">96h"]
    operational_buckets = defaultdict(int)
    carrier_buckets = defaultdict(int)
    has_invalid = False

    rows = queryset.values_list("operational_lead_time_hours", "carrier_lead_time_hours")
    for operational_hours, carrier_hours in rows:
        operational_bucket = _get_lead_time_bucket(operational_hours)
        carrier_bucket = _get_lead_time_bucket(carrier_hours)
        if operational_bucket:
            operational_buckets[operational_bucket] += 1
            has_invalid = has_invalid or operational_bucket == "Invalido"
        if carrier_bucket:
            carrier_buckets[carrier_bucket] += 1
            has_invalid = has_invalid or carrier_bucket == "Invalido"

    if has_invalid:
        bucket_labels = ["Invalido"] + bucket_labels

    return make_chart_contract(
        chart_id="lead_time_distribution",
        title="Distribuicao de lead time",
        chart_type="bar",
        labels=bucket_labels,
        datasets=[
            {
                "label": "Operacional",
                "data": [operational_buckets[label] for label in bucket_labels],
            },
            {
                "label": "Transportadora",
                "data": [carrier_buckets[label] for label in bucket_labels],
            },
        ],
    )


def _get_dimension_lead_time_comparison_chart(rows, chart_id, title, metadata_key):
    chart_rows = rows[:TOP_GROUP_LIMIT]

    return make_chart_contract(
        chart_id=chart_id,
        title=title,
        chart_type="bar",
        labels=[row["label"] for row in chart_rows],
        datasets=[
            {
                "label": "LT operacional medio",
                "data": [
                    _to_float(row["average_operational_lead_time_hours_raw"])
                    for row in chart_rows
                ],
            },
            {
                "label": "LT transportadora medio",
                "data": [
                    _to_float(row["average_carrier_lead_time_hours_raw"])
                    for row in chart_rows
                ],
            },
            {
                "label": "Atraso operacional %",
                "data": [_to_float(row["operational_late_percentage_raw"]) for row in chart_rows],
            },
            {
                "label": "Atraso transportadora %",
                "data": [_to_float(row["carrier_late_percentage_raw"]) for row in chart_rows],
            },
        ],
        options={
            "scales": {
                "y": {
                    "beginAtZero": True,
                }
            }
        },
        metadata=[_format_group_metadata(row, metadata_key) for row in chart_rows],
    )


def _get_driver_outliers_table(queryset, driver_rows):
    p90_by_driver = _get_group_p90_map(queryset, "driver_name", "operational_lead_time_hours")

    return [
        {
            "driver_name": row["label"],
            "total_records": row["total_records"],
            "delivered_records": row["delivered_records"],
            "delayed_records": row["delayed_records"],
            "total_invoice_value": _format_decimal(row["total_invoice_value_raw"]),
            "delay_severity_hours": _format_decimal(row["delay_severity_hours_raw"]),
            "average_operational_lead_time_hours": _format_decimal(
                row["average_operational_lead_time_hours_raw"]
            ),
            "operational_lead_time_p90_hours": _format_decimal(
                p90_by_driver.get(row["group_value"], Decimal("0"))
            ),
            "average_carrier_lead_time_hours": _format_decimal(
                row["average_carrier_lead_time_hours_raw"]
            ),
            "operational_late_percentage": _format_decimal(row["operational_late_percentage_raw"]),
            "carrier_late_percentage": _format_decimal(row["carrier_late_percentage_raw"]),
            "criticality_score": _format_decimal(row["criticality_score_raw"]),
        }
        for row in driver_rows[:TOP_GROUP_LIMIT]
    ]


def _get_critical_routes_table(queryset, route_rows):
    p90_by_route = _get_group_p90_map(queryset, "route", "operational_lead_time_hours")

    return [
        {
            "route": row["label"],
            "total_records": row["total_records"],
            "delivered_records": row["delivered_records"],
            "delayed_records": row["delayed_records"],
            "served_cities": row["served_cities"],
            "total_invoice_value": _format_decimal(row["total_invoice_value_raw"]),
            "delay_severity_hours": _format_decimal(row["delay_severity_hours_raw"]),
            "average_operational_lead_time_hours": _format_decimal(
                row["average_operational_lead_time_hours_raw"]
            ),
            "operational_lead_time_p90_hours": _format_decimal(
                p90_by_route.get(row["group_value"], Decimal("0"))
            ),
            "operational_late_percentage": _format_decimal(row["operational_late_percentage_raw"]),
            "carrier_late_percentage": _format_decimal(row["carrier_late_percentage_raw"]),
            "criticality_score": _format_decimal(row["criticality_score_raw"]),
        }
        for row in route_rows[:TOP_GROUP_LIMIT]
    ]


def _get_critical_cities_table(city_rows):
    return [
        {
            "city": row["label"],
            "total_records": row["total_records"],
            "routes": row["routes"],
            "delayed_records": row["delayed_records"],
            "total_invoice_value": _format_decimal(row["total_invoice_value_raw"]),
            "delay_severity_hours": _format_decimal(row["delay_severity_hours_raw"]),
            "average_operational_lead_time_hours": _format_decimal(
                row["average_operational_lead_time_hours_raw"]
            ),
            "average_carrier_lead_time_hours": _format_decimal(
                row["average_carrier_lead_time_hours_raw"]
            ),
            "operational_late_percentage": _format_decimal(row["operational_late_percentage_raw"]),
            "carrier_late_percentage": _format_decimal(row["carrier_late_percentage_raw"]),
            "criticality_score": _format_decimal(row["criticality_score_raw"]),
        }
        for row in city_rows[:TOP_GROUP_LIMIT]
    ]


def _get_critical_dimension_table(rows, key_name):
    return [
        {
            key_name: row["label"],
            "total_records": row["total_records"],
            "delayed_records": row["delayed_records"],
            "total_invoice_value": _format_decimal(row["total_invoice_value_raw"]),
            "average_operational_lead_time_hours": _format_decimal(
                row["average_operational_lead_time_hours_raw"]
            ),
            "average_carrier_lead_time_hours": _format_decimal(
                row["average_carrier_lead_time_hours_raw"]
            ),
            "delay_severity_hours": _format_decimal(row["delay_severity_hours_raw"]),
            "operational_late_percentage": _format_decimal(row["operational_late_percentage_raw"]),
            "carrier_late_percentage": _format_decimal(row["carrier_late_percentage_raw"]),
            "criticality_score": _format_decimal(row["criticality_score_raw"]),
        }
        for row in rows[:TOP_GROUP_LIMIT]
    ]


def _get_invoice_outliers_table(queryset):
    rows = (
        queryset.filter(
            Q(operational_lead_time_hours__isnull=False) | Q(carrier_lead_time_hours__isnull=False)
        )
        .order_by("-operational_lead_time_hours", "-carrier_lead_time_hours", "invoice_number")[:20]
        .values(
            "invoice_number",
            "invoice_series",
            "driver_name",
            "route",
            "city",
            "invoice_value",
            "invoice_issue_date",
            "customer_delivery_date",
            "operational_lead_time_hours",
            "carrier_lead_time_hours",
            "cargo_status",
            "delivery_status",
        )
    )

    return [
        {
            "invoice_number": row["invoice_number"],
            "invoice_series": row["invoice_series"],
            "driver_name": row["driver_name"] or "Sem motorista",
            "route": row["route"] or "Sem pauta",
            "city": row["city"] or "Sem cidade",
            "invoice_value": _format_decimal(row["invoice_value"]),
            "invoice_issue_date": _format_date(row["invoice_issue_date"]),
            "customer_delivery_date": _format_date(row["customer_delivery_date"]),
            "operational_lead_time_hours": _format_decimal(row["operational_lead_time_hours"]),
            "carrier_lead_time_hours": _format_decimal(row["carrier_lead_time_hours"]),
            "cargo_status": row["cargo_status"],
            "delivery_status": row["delivery_status"],
        }
        for row in rows
    ]


def _get_status_inconsistencies_table(queryset):
    rows = (
        queryset.filter(_get_status_inconsistency_filter())
        .order_by("-customer_delivery_date", "-invoice_issue_date", "invoice_number")[:20]
        .values(
            "invoice_number",
            "invoice_series",
            "driver_name",
            "route",
            "city",
            "invoice_issue_date",
            "customer_delivery_date",
            "cargo_status",
            "delivery_status",
            "operational_lead_time_hours",
            "carrier_lead_time_hours",
        )
    )

    return [
        {
            "invoice_number": row["invoice_number"],
            "invoice_series": row["invoice_series"],
            "driver_name": row["driver_name"] or "Sem motorista",
            "route": row["route"] or "Sem pauta",
            "city": row["city"] or "Sem cidade",
            "invoice_issue_date": _format_date(row["invoice_issue_date"]),
            "customer_delivery_date": _format_date(row["customer_delivery_date"]),
            "cargo_status": row["cargo_status"],
            "delivery_status": row["delivery_status"],
            "operational_lead_time_hours": _format_decimal(row["operational_lead_time_hours"]),
            "carrier_lead_time_hours": _format_decimal(row["carrier_lead_time_hours"]),
        }
        for row in rows
    ]


def _get_criticality_totals(queryset):
    aggregates = queryset.aggregate(
        total_records=Count("id"),
        total_delayed_records=Count("id", filter=DELAYED_RECORDS_LOOKUP),
        total_invoice_value=Sum("invoice_value"),
    )
    total_delay_severity_hours = sum(
        _get_delay_severity(operational_hours, carrier_hours)
        for operational_hours, carrier_hours in queryset.values_list(
            "operational_lead_time_hours",
            "carrier_lead_time_hours",
        )
    )
    return {
        "total_records": aggregates["total_records"] or 0,
        "total_delayed_records": aggregates["total_delayed_records"] or 0,
        "total_invoice_value": aggregates["total_invoice_value"] or Decimal("0"),
        "total_delay_severity_hours": total_delay_severity_hours,
    }


def _get_group_criticality_rows(
    queryset,
    group_field,
    empty_label,
    totals,
    include_empty_groups=True,
):
    severity_by_group = _get_group_delay_severity_map(queryset, group_field)
    rows = list(
        queryset.values(group_field)
        .annotate(
            total_records=Count("id"),
            delivered_records=Count("id", filter=DELIVERED_STATUS_LOOKUP),
            delayed_records=Count("id", filter=DELAYED_RECORDS_LOOKUP),
            operational_late_records=Count("id", filter=Q(is_operational_late=True)),
            carrier_late_records=Count("id", filter=Q(is_carrier_late=True)),
            total_invoice_value=Sum("invoice_value"),
            average_operational_lead_time_hours=Avg("operational_lead_time_hours"),
            average_carrier_lead_time_hours=Avg("carrier_lead_time_hours"),
            served_cities=Count("city", distinct=True),
            routes=Count("route", distinct=True),
        )
    )

    normalized_rows = []
    for row in rows:
        group_value = row[group_field] or ""
        if not include_empty_groups and not group_value:
            continue

        total_records = row["total_records"] or 0
        delayed_records = row["delayed_records"] or 0
        total_invoice_value = row["total_invoice_value"] or Decimal("0")
        delay_severity_hours = severity_by_group.get(group_value, Decimal("0"))
        records_share = _safe_divide(total_records, totals["total_records"])
        delayed_share = _safe_divide(delayed_records, totals["total_delayed_records"])
        value_share = _safe_divide(total_invoice_value, totals["total_invoice_value"])
        severity_share = _safe_divide(
            delay_severity_hours,
            totals["total_delay_severity_hours"],
        )
        criticality_score = (
            (records_share * Decimal("0.20"))
            + (delayed_share * Decimal("0.30"))
            + (value_share * Decimal("0.20"))
            + (severity_share * Decimal("0.30"))
        ) * Decimal("100")

        normalized_rows.append(
            {
                "group_value": group_value,
                "label": row[group_field] or empty_label,
                "total_records": total_records,
                "delivered_records": row["delivered_records"] or 0,
                "delayed_records": delayed_records,
                "operational_late_records": row["operational_late_records"] or 0,
                "carrier_late_records": row["carrier_late_records"] or 0,
                "total_invoice_value_raw": total_invoice_value,
                "delay_severity_hours_raw": delay_severity_hours,
                "average_operational_lead_time_hours_raw": row[
                    "average_operational_lead_time_hours"
                ]
                or Decimal("0"),
                "average_carrier_lead_time_hours_raw": row["average_carrier_lead_time_hours"]
                or Decimal("0"),
                "operational_late_percentage_raw": _safe_divide(
                    (row["operational_late_records"] or 0) * 100,
                    total_records,
                ),
                "carrier_late_percentage_raw": _safe_divide(
                    (row["carrier_late_records"] or 0) * 100,
                    total_records,
                ),
                "delayed_percentage_raw": _safe_divide(delayed_records * 100, total_records),
                "criticality_score_raw": _quantize_decimal(criticality_score),
                "served_cities": row["served_cities"] or 0,
                "routes": row["routes"] or 0,
            }
        )

    normalized_rows.sort(
        key=lambda row: (
            -row["criticality_score_raw"],
            -row["total_records"],
            row["label"],
        )
    )

    min_group_size = _get_min_group_size(totals["total_records"])
    filtered_rows = [row for row in normalized_rows if row["total_records"] >= min_group_size]
    return filtered_rows or normalized_rows


def _get_group_delay_severity_map(queryset, group_field):
    severity_by_group = defaultdict(Decimal)
    rows = queryset.values_list(
        group_field,
        "operational_lead_time_hours",
        "carrier_lead_time_hours",
    )
    for group_value, operational_hours, carrier_hours in rows:
        severity_by_group[group_value or ""] += _get_delay_severity(
            operational_hours,
            carrier_hours,
        )
    return severity_by_group


def _get_delay_severity(operational_hours, carrier_hours):
    operational_delay = max(
        Decimal(operational_hours or 0) - OPERATIONAL_TARGET_HOURS,
        Decimal("0"),
    )
    carrier_delay = max(
        Decimal(carrier_hours or 0) - CARRIER_TARGET_HOURS,
        Decimal("0"),
    )
    return operational_delay + carrier_delay


def _get_group_p90_map(queryset, group_field, lead_time_field):
    grouped_values = defaultdict(list)
    rows = (
        queryset.exclude(**{f"{lead_time_field}__isnull": True})
        .order_by(group_field, lead_time_field)
        .values_list(group_field, lead_time_field)
    )
    for group_value, lead_time_value in rows:
        grouped_values[group_value or ""].append(lead_time_value)

    return {
        group_value: _get_percentile(values, 90)
        for group_value, values in grouped_values.items()
    }


def _get_status_inconsistency_filter():
    return DELIVERED_STATUS_LOOKUP & (
        Q(cargo_status="")
        | Q(cargo_status__isnull=True)
        | ~Q(cargo_status__icontains="entreg")
    )


def _get_min_group_size(total_records):
    if total_records < 100:
        return 1
    return max(10, int(total_records * 0.005))


def _get_percentile(values, percentile):
    values = [Decimal(value) for value in values if value is not None]
    if not values:
        return Decimal("0")

    values.sort()
    index = max(ceil((Decimal(percentile) / Decimal("100")) * len(values)) - 1, 0)
    return values[index]


def _format_critical_route_card(row):
    if not row:
        return {
            "route": "Sem dados",
            "criticality_score": "0.00",
            "total_records": 0,
            "delayed_percentage": "0.00",
            "delay_severity_hours": "0.00",
        }

    return {
        "route": row["label"],
        "criticality_score": _format_decimal(row["criticality_score_raw"]),
        "total_records": row["total_records"],
        "delayed_percentage": _format_decimal(row["delayed_percentage_raw"]),
        "delay_severity_hours": _format_decimal(row["delay_severity_hours_raw"]),
    }


def _format_group_metadata(row, key_name):
    return {
        key_name: row["label"],
        "total_records": row["total_records"],
        "delayed_records": row["delayed_records"],
        "total_invoice_value": _format_decimal(row["total_invoice_value_raw"]),
        "delay_severity_hours": _format_decimal(row["delay_severity_hours_raw"]),
        "average_operational_lead_time_hours": _format_decimal(
            row["average_operational_lead_time_hours_raw"]
        ),
        "average_carrier_lead_time_hours": _format_decimal(
            row["average_carrier_lead_time_hours_raw"]
        ),
        "operational_late_percentage": _format_decimal(row["operational_late_percentage_raw"]),
        "carrier_late_percentage": _format_decimal(row["carrier_late_percentage_raw"]),
        "criticality_score": _format_decimal(row["criticality_score_raw"]),
    }


def _get_bubble_radius(value, max_value):
    if not max_value:
        return 6

    ratio = _safe_divide(value, max_value)
    radius = Decimal("5") + (ratio * Decimal("13"))
    return float(_quantize_decimal(max(Decimal("5"), min(radius, Decimal("18")))))


def _get_lead_time_bucket(value):
    if value is None:
        return None

    value = Decimal(value)
    if value < 0:
        return "Invalido"
    if value <= 24:
        return "0-24h"
    if value <= 48:
        return "24-48h"
    if value <= 72:
        return "48-72h"
    if value <= 96:
        return "72-96h"
    return ">96h"


def _get_last_successful_import():
    batch = (
        ImportBatch.objects.filter(status=ImportBatch.Status.SUCCESS)
        .order_by("-finished_at", "-started_at", "-id")
        .first()
    )

    if not batch:
        return None

    return {
        "id": batch.id,
        "file_name": batch.file_name,
        "source_mode": batch.source_mode,
        "status": batch.status,
        "started_at": batch.started_at.isoformat() if batch.started_at else None,
        "finished_at": batch.finished_at.isoformat() if batch.finished_at else None,
        "total_rows": batch.total_rows,
        "valid_rows": batch.valid_rows,
        "invalid_rows": batch.invalid_rows,
    }


def _safe_divide(numerator, denominator):
    denominator = Decimal(denominator or 0)
    if denominator == 0:
        return Decimal("0")
    return Decimal(numerator or 0) / denominator


def _format_decimal(value):
    return str(_quantize_decimal(value))


def _format_percentage(count, total):
    return _format_decimal(_safe_divide(Decimal(count) * Decimal("100"), total))


def _to_float(value):
    return float(_quantize_decimal(value))


def _quantize_decimal(value):
    value = Decimal(value or 0)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _format_date(value):
    if value is None:
        return ""
    return value.isoformat()
