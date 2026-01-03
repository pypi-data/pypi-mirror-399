from django.template import Library

register = Library()


@register.simple_tag(name='print')
def print_(*values, sep: str = ' ', end: str = '\n'):
    print(*values, sep=sep, end=end)
    return ''
