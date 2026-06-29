from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from django.utils.dateparse import parse_date


@dataclass(frozen=True)
class DashboardFilters:
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    driver_name: List[str] = field(default_factory=list)
    route: List[str] = field(default_factory=list)
    business_unit: List[str] = field(default_factory=list)
    region: List[str] = field(default_factory=list)
    frequency: List[str] = field(default_factory=list)
    delivery_status: List[str] = field(default_factory=list)
    cargo_status: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        for field_name in _MULTI_VALUE_FIELDS:
            object.__setattr__(self, field_name, _clean_values(getattr(self, field_name)))

    @classmethod
    def from_querydict(cls, querydict):
        errors = []
        date_start = _parse_optional_date(querydict.get("date_start"), "date_start", errors)
        date_end = _parse_optional_date(querydict.get("date_end"), "date_end", errors)

        return cls(
            date_start=date_start,
            date_end=date_end,
            driver_name=_get_query_values(querydict, "driver_name"),
            route=_get_query_values(querydict, "route"),
            business_unit=_get_query_values(querydict, "business_unit"),
            region=_get_query_values(querydict, "region"),
            frequency=_get_query_values(querydict, "frequency"),
            delivery_status=_get_query_values(querydict, "delivery_status"),
            cargo_status=_get_query_values(querydict, "cargo_status"),
            errors=errors,
        )

    def apply_to_queryset(self, queryset):
        if self.date_start:
            queryset = queryset.filter(invoice_issue_date__gte=self.date_start)
        if self.date_end:
            queryset = queryset.filter(invoice_issue_date__lte=self.date_end)
        if self.driver_name:
            queryset = queryset.filter(driver_name__in=self.driver_name)
        if self.route:
            queryset = queryset.filter(route__in=self.route)
        if self.business_unit:
            queryset = queryset.filter(business_unit__in=self.business_unit)
        if self.region:
            queryset = queryset.filter(region__in=self.region)
        if self.frequency:
            queryset = queryset.filter(frequency__in=self.frequency)
        if self.delivery_status:
            queryset = queryset.filter(delivery_status__in=self.delivery_status)
        if self.cargo_status:
            queryset = queryset.filter(cargo_status__in=self.cargo_status)
        return queryset

    def as_dict(self):
        return {
            "date_start": self.date_start.isoformat() if self.date_start else "",
            "date_end": self.date_end.isoformat() if self.date_end else "",
            "driver_name": self.driver_name,
            "route": self.route,
            "business_unit": self.business_unit,
            "region": self.region,
            "frequency": self.frequency,
            "delivery_status": self.delivery_status,
            "cargo_status": self.cargo_status,
        }


_MULTI_VALUE_FIELDS = (
    "driver_name",
    "route",
    "business_unit",
    "region",
    "frequency",
    "delivery_status",
    "cargo_status",
)


def _get_query_values(querydict, field_name):
    if hasattr(querydict, "getlist"):
        return _clean_values(querydict.getlist(field_name))

    return _clean_values(querydict.get(field_name))


def _clean_values(values):
    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    return [
        cleaned_value
        for cleaned_value in (_clean_value(value) for value in values)
        if cleaned_value is not None
    ]


def _clean_value(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _parse_optional_date(value, field_name, errors):
    value = _clean_value(value)
    if not value:
        return None

    parsed_value = parse_date(value)
    if parsed_value is None:
        errors.append(f"{field_name} must use YYYY-MM-DD.")
    return parsed_value
