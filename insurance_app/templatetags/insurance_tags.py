from django import template

register = template.Library()

@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key, '')
    elif isinstance(value, (list, tuple)) and isinstance(key, int):
        try:
            return value[key]
        except IndexError:
            return ''
    return '' 