from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from django.utils.dateparse import parse_date


@dataclass(frozen=True)
class DashboardFilters:
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    driver_name: Optional[str] = None
    route: Optional[str] = None
    business_unit: Optional[str] = None
    delivery_status: Optional[str] = None
    cargo_status: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    @classmethod
    def from_querydict(cls, querydict):
        errors = []
        date_start = _parse_optional_date(querydict.get("date_start"), "date_start", errors)
        date_end = _parse_optional_date(querydict.get("date_end"), "date_end", errors)

        return cls(
            date_start=date_start,
            date_end=date_end,
            driver_name=_clean_value(querydict.get("driver_name")),
            route=_clean_value(querydict.get("route")),
            business_unit=_clean_value(querydict.get("business_unit")),
            delivery_status=_clean_value(querydict.get("delivery_status")),
            cargo_status=_clean_value(querydict.get("cargo_status")),
            errors=errors,
        )

    def apply_to_queryset(self, queryset):
        if self.date_start:
            queryset = queryset.filter(invoice_issue_date__gte=self.date_start)
        if self.date_end:
            queryset = queryset.filter(invoice_issue_date__lte=self.date_end)
        if self.driver_name:
            queryset = queryset.filter(driver_name=self.driver_name)
        if self.route:
            queryset = queryset.filter(route=self.route)
        if self.business_unit:
            queryset = queryset.filter(business_unit=self.business_unit)
        if self.delivery_status:
            queryset = queryset.filter(delivery_status=self.delivery_status)
        if self.cargo_status:
            queryset = queryset.filter(cargo_status=self.cargo_status)
        return queryset

    def as_dict(self):
        return {
            "date_start": self.date_start.isoformat() if self.date_start else "",
            "date_end": self.date_end.isoformat() if self.date_end else "",
            "driver_name": self.driver_name or "",
            "route": self.route or "",
            "business_unit": self.business_unit or "",
            "delivery_status": self.delivery_status or "",
            "cargo_status": self.cargo_status or "",
        }


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
