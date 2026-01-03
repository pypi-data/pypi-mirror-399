from typing import Literal, Callable
from functools import wraps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, JsonResponse
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods as django_require_http_methods
from .exceptions import Http401


def require_http_methods(*methods: Literal['GET', 'POST', 'PUT', 'DELETE'], error_mode: bool = True) -> Callable:
    def decorator(view_function):
        @wraps(view_function)
        def if_error(request, *args, **kwargs):
            return django_require_http_methods(methods)(view_function)(request, *args, **kwargs)

        @wraps(view_function)
        def not_error(request, *args, **kwargs):
            pass

        return if_error if error_mode else not_error


def debug_required(func):
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            raise ImproperlyConfigured('Only debug mode is on')
        return func(*args, **kwargs)
    return wrapper
