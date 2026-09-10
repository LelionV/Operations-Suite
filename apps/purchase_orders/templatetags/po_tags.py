from django import template
register = template.Library()

@register.filter
def contains(lst, val):
    """Check if val is in lst (for template use)."""
    try:
        return val in lst
    except TypeError:
        return False
