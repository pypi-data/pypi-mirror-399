from django.apps import AppConfig


class HrendjangoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hrendjango'
    verbose_name = 'Модели HrenDjango'
    default_settings = dict(
        HRENDJANGO_ACTIVE_MODELS='all',
        HRENDJANGO_FILE_MODEL='hrendjango.MediaFile',
        HRENDJANGO_IMAGE_MODEL='hrendjango.ImageMediaFile'
    )

    def ready(self):
        from django.conf import settings
        for key, value in self.default_settings.items():
            setattr(settings, key, getattr(settings, key, value))
