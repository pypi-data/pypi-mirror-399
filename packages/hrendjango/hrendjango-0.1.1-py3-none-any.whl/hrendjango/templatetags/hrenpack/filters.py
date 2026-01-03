import xml.etree.ElementTree as ElementTree
from typing import Union, Optional
from django.template import Library
from hrenpack import IntStr
from hrenpack.filework.xml import XMLParser
from rusgram import pluralize

register = Library()


@register.filter
def get_item(dictionary, key, default=None):
    return dictionary.get(key, default)


@register.filter
def svg_to_html(value):
    svg = XMLParser(value).find('svg')
    return str(svg)


@register.filter
def addition(value, arg):
    return value + arg


@register.filter
def as_int(value):
    return int(value)


"""
@register.filter
def word_format(value: Union[IntStr, float], word: str) -> str:
    if isinstance(value, str):
        value = int(value)
    elif isinstance(value, float):
        return f'{value} {word}ов'
    else:
        match str(value)[-1]:
            case '1':
                return f'{value} {word}'
            case '2' | '3' | '4':
                return f'{value} {word}а'
            case _:
                return f'{value} {word}ов'
"""


@register.filter
def word_format(value: int, word: str) -> str:
    return pluralize(value, word)


@register.filter
def true_false(value):
    return str(value).lower()
