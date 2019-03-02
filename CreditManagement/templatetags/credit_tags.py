from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def euro(value):
    """Format for euro values."""
    amount = "{:.3f}".format(abs(value))
    v = "{}€{}".format('-' if value < 0 else '', amount)
    return mark_safe(v)


@register.filter
def negate(value):
    """Negates given numeric value."""
    return -value