from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from hrenpack.framework.django.views import *


def robots_txt(request):
    path = settings.BASE_DIR / 'robots.txt'
    if not path.is_file():
        raise Http404


