from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from django.db.models import Avg, Count, Q, Sum

from imports.models import ImportBatch, LeadTimeRecord

from .chart_contracts import make_chart_contract, make_single_dataset_chart
from .dashboard_filters import DashboardFilters


DELIVERED_STATUS_LOOKUP = Q(delivery_status__icontains="entreg")
TOP_GROUP_LIMIT = 10


def get_dashboard_context(filters: Optional[DashboardFilters] = None):
    filters = filters or DashboardFilters()
    base_queryset = LeadTimeRecord.objects.select_related("import_batch")
    filtered_queryset = filters.apply_to_queryset(base_queryset)

    cards = _get_cards(filtered_queryset)

    return {
        "filters": filters.as_dict(),
        "filter_errors": filters.errors,
        "filter_options": _get_filter_options(),
        "cards": cards,
        "charts": {
            "records_by_day": _get_records_by_day_chart(filtered_queryset),
            "records_by_driver": _get_records_by_driver_chart(filtered_queryset),
            "records_by_route": _get_records_by_route_chart(filtered_queryset),
            "delivery_status_distribution": _get_delivery_status_distribution_chart(filtered_queryset),
            "lead_time_by_driver": _get_lead_time_by_driver_chart(filtered_queryset),
        },
        "tables": {
            "driver_summary": _get_driver_summary(filtered_queryset),
            "route_summary": _get_route_summary(filtered_queryset),
        },
        "metadata": {
            "last_successful_import": _get_last_successful_import(),
            "has_data": cards["total_records"] > 0,
        },
    }


def _get_cards(queryset):
    aggregates = queryset.aggregate(
        total_records=Count("id"),
        delivered_records=Count("id", filter=DELIVERED_STATUS_LOOKUP),
        total_invoice_value=Sum("invoice_value"),
        average_operational_lead_time_hours=Avg("operational_lead_time_hours"),
        average_carrier_lead_time_hours=Avg("carrier_lead_time_hours"),
        operational_late_records=Count("id", filter=Q(is_operational_late=True)),
        carrier_late_records=Count("id", filter=Q(is_carrier_late=True)),
    )

    total_records = aggregates["total_records"] or 0
    delivered_records = aggregates["delivered_records"] or 0
    operational_late_records = aggregates["operational_late_records"] or 0
    carrier_late_records = aggregates["carrier_late_records"] or 0

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
    }


def _get_filter_options():
    return {
        "drivers": _get_distinct_values("driver_name"),
        "routes": _get_distinct_values("route"),
        "business_units": _get_distinct_values("business_unit"),
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


def _get_records_by_driver_chart(queryset):
    rows = _group_count(queryset, "driver_name")

    return make_single_dataset_chart(
        chart_id="records_by_driver",
        title="Registros por motorista",
        chart_type="bar",
        labels=[row["driver_name"] or "Sem motorista" for row in rows],
        label="Registros",
        data=[row["total"] for row in rows],
    )


def _get_records_by_route_chart(queryset):
    rows = _group_count(queryset, "route")

    return make_single_dataset_chart(
        chart_id="records_by_route",
        title="Registros por pauta",
        chart_type="bar",
        labels=[row["route"] or "Sem pauta" for row in rows],
        label="Registros",
        data=[row["total"] for row in rows],
    )


def _get_delivery_status_distribution_chart(queryset):
    rows = _group_count(queryset, "delivery_status")

    return make_single_dataset_chart(
        chart_id="delivery_status_distribution",
        title="Distribuicao por status de entrega",
        chart_type="doughnut",
        labels=[row["delivery_status"] or "Sem status" for row in rows],
        label="Registros",
        data=[row["total"] for row in rows],
    )


def _get_lead_time_by_driver_chart(queryset):
    rows = (
        queryset.exclude(driver_name="")
        .values("driver_name")
        .annotate(
            total=Count("id"),
            average_operational=Avg("operational_lead_time_hours"),
            average_carrier=Avg("carrier_lead_time_hours"),
        )
        .order_by("-total", "driver_name")[:TOP_GROUP_LIMIT]
    )

    return make_chart_contract(
        chart_id="lead_time_by_driver",
        title="Lead time medio por motorista",
        chart_type="bar",
        labels=[row["driver_name"] for row in rows],
        datasets=[
            {
                "label": "Operacional",
                "data": [_to_float(row["average_operational"]) for row in rows],
            },
            {
                "label": "Transportadora",
                "data": [_to_float(row["average_carrier"]) for row in rows],
            },
        ],
    )


def _get_driver_summary(queryset):
    rows = (
        queryset.values("driver_name")
        .annotate(
            total_records=Count("id"),
            delivered_records=Count("id", filter=DELIVERED_STATUS_LOOKUP),
            operational_late_records=Count("id", filter=Q(is_operational_late=True)),
            carrier_late_records=Count("id", filter=Q(is_carrier_late=True)),
            total_invoice_value=Sum("invoice_value"),
            average_operational_lead_time_hours=Avg("operational_lead_time_hours"),
            average_carrier_lead_time_hours=Avg("carrier_lead_time_hours"),
        )
        .order_by("-total_records", "driver_name")[:TOP_GROUP_LIMIT]
    )

    return [
        {
            "driver_name": row["driver_name"] or "Sem motorista",
            "total_records": row["total_records"],
            "delivered_records": row["delivered_records"],
            "pending_records": row["total_records"] - row["delivered_records"],
            "operational_late_records": row["operational_late_records"],
            "carrier_late_records": row["carrier_late_records"],
            "total_invoice_value": _format_decimal(row["total_invoice_value"]),
            "average_operational_lead_time_hours": _format_decimal(
                row["average_operational_lead_time_hours"]
            ),
            "average_carrier_lead_time_hours": _format_decimal(
                row["average_carrier_lead_time_hours"]
            ),
        }
        for row in rows
    ]


def _get_route_summary(queryset):
    rows = (
        queryset.values("route")
        .annotate(
            total_records=Count("id"),
            delivered_records=Count("id", filter=DELIVERED_STATUS_LOOKUP),
            operational_late_records=Count("id", filter=Q(is_operational_late=True)),
            carrier_late_records=Count("id", filter=Q(is_carrier_late=True)),
            total_invoice_value=Sum("invoice_value"),
            average_operational_lead_time_hours=Avg("operational_lead_time_hours"),
            average_carrier_lead_time_hours=Avg("carrier_lead_time_hours"),
        )
        .order_by("-total_records", "route")[:TOP_GROUP_LIMIT]
    )

    return [
        {
            "route": row["route"] or "Sem pauta",
            "total_records": row["total_records"],
            "delivered_records": row["delivered_records"],
            "pending_records": row["total_records"] - row["delivered_records"],
            "operational_late_records": row["operational_late_records"],
            "carrier_late_records": row["carrier_late_records"],
            "total_invoice_value": _format_decimal(row["total_invoice_value"]),
            "average_operational_lead_time_hours": _format_decimal(
                row["average_operational_lead_time_hours"]
            ),
            "average_carrier_lead_time_hours": _format_decimal(
                row["average_carrier_lead_time_hours"]
            ),
        }
        for row in rows
    ]


def _group_count(queryset, field_name):
    return (
        queryset.values(field_name)
        .annotate(total=Count("id"))
        .order_by("-total", field_name)[:TOP_GROUP_LIMIT]
    )


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


def _format_decimal(value):
    value = value or Decimal("0")
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _format_percentage(count, total):
    if not total:
        return "0.00"
    return _format_decimal((Decimal(count) * Decimal("100")) / Decimal(total))


def _to_float(value):
    value = value or Decimal("0")
    return float(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _format_date(value):
    if value is None:
        return ""
    return value.isoformat()
