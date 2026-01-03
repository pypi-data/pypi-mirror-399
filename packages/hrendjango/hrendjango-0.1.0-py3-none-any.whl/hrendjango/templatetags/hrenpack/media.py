from django.template import Library
from django.conf import settings

register = Library()


@register.simple_tag
def media(url: str):
    return settings.MEDIA_URL + url
