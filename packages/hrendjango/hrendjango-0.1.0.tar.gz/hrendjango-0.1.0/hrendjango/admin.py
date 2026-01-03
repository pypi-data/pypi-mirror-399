from django.conf import settings
from django.contrib import admin
from .models import get_file_model, get_image_model


if getattr(settings, 'HRENDJANGO_ACTIVE_MODELS', None):
    admin.site.register(get_file_model())
    admin.site.register(get_image_model())
