from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    try:
        val = float(value)
        factor = float(arg)
        res = val * factor
        if res.is_integer():
            return int(res)
        return res
    except (ValueError, TypeError):
        return 0
