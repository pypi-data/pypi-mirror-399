from django.http import Http404
from django.core.exceptions import *


class Http400(SuspiciousOperation):
    pass


class Http401(Exception):
    pass


class Http403(PermissionDenied):
    pass


class Http405(Exception):
    pass


class HttpLog405(Exception):
    pass
