from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP


OPERATIONAL_TARGET_HOURS = Decimal("48.00")
CARRIER_TARGET_HOURS = Decimal("24.00")


def calculate_business_hours(start_datetime, end_datetime):
    if not start_datetime or not end_datetime:
        return None

    direction = Decimal("1")
    start = start_datetime
    end = end_datetime
    if end < start:
        start, end = end, start
        direction = Decimal("-1")

    total_seconds = 0
    cursor = start
    while cursor < end:
        next_day = datetime.combine(
            cursor.date() + timedelta(days=1),
            time.min,
            tzinfo=cursor.tzinfo,
        )
        segment_end = min(next_day, end)
        if cursor.weekday() < 5:
            total_seconds += (segment_end - cursor).total_seconds()
        cursor = segment_end

    hours = Decimal(str(total_seconds / 3600))
    return (hours * direction).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_lead_times(invoice_issue_datetime, load_datetime, delivery_datetime):
    operational_hours = calculate_business_hours(invoice_issue_datetime, delivery_datetime)
    carrier_hours = calculate_business_hours(load_datetime, delivery_datetime)

    return {
        "operational_lead_time_hours": operational_hours,
        "carrier_lead_time_hours": carrier_hours,
        "is_operational_late": (
            operational_hours is not None
            and operational_hours > OPERATIONAL_TARGET_HOURS
        ),
        "is_carrier_late": (
            carrier_hours is not None
            and carrier_hours > CARRIER_TARGET_HOURS
        ),
        "business_days_count": _business_days_count(invoice_issue_datetime, delivery_datetime),
    }


def _business_days_count(start_datetime, end_datetime):
    if not start_datetime or not end_datetime:
        return None

    start_date = min(start_datetime.date(), end_datetime.date())
    end_date = max(start_datetime.date(), end_datetime.date())
    count = 0
    cursor = start_date
    while cursor <= end_date:
        if cursor.weekday() < 5:
            count += 1
        cursor += timedelta(days=1)
    return count
