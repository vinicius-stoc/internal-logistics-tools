from django import template

from accounts.services.access_label_service import get_group_display_name


register = template.Library()


@register.filter
def group_display_name(group_name):
    return get_group_display_name(group_name)
