from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template
from django.utils.html import format_html


register = template.Library()


def _to_decimal(value):
    if value is None or value == "":
        return Decimal("0")

    if isinstance(value, Decimal):
        return value

    normalized = str(value).strip()
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    try:
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _format_decimal(value, decimal_places=2):
    decimal_places = int(decimal_places)
    quantizer = Decimal("1") if decimal_places == 0 else Decimal(f"1.{'0' * decimal_places}")
    number = _to_decimal(value).quantize(quantizer, rounding=ROUND_HALF_UP)
    formatted = f"{number:,.{decimal_places}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


@register.filter
def br_currency(value):
    return format_html("R$&nbsp;{}", _format_decimal(value, 2))


@register.filter
def br_number(value, decimal_places=0):
    return _format_decimal(value, decimal_places)


@register.filter
def br_percent(value, decimal_places=2):
    return format_html("{}%", _format_decimal(value, decimal_places))
