from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """{{ my_dict|get_item:key }}"""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None
