from importlib import import_module
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from hrenpack.framework.django import *
from django.apps import apps
from django.conf import settings
from django.db import migrations
from django.core.exceptions import ImproperlyConfigured
from . import translator


def create_model(
    name: Any,
    fields: Any,
    options: Any = None,
    bases: Any = None,
    managers: Any = None
):
    models = settings.HRENDJANGO_ACTIVE_MODELS
    if name in models or models == 'all':
        return migrations.CreateModel(name, fields, options, bases, managers)


def get_model(setting_name: str):
    setting_name = setting_name.upper()
    setting = getattr(settings, setting_name)
    try:
        return apps.get_model(setting, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(f"{setting_name} must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(f"{setting_name} refers to model '%s' that has not been installed" % setting)


def get_project_name():
    return settings.ROOT_URLCONF.split('.')[0]


def safe_get_user_model():
    try:
        return get_user_model()
    except ImproperlyConfigured:
        return settings.AUTH_USER_MODEL


def translate_text(text, output_lang: [Optional[str]] = None, input_lang: str = 'auto'):
    if output_lang is None:
        output_lang = settings.LANGUAGE_CODE.split('-')[0]
    return translator.translate(text, src=input_lang, dest=output_lang).text
