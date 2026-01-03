from django import forms
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from hrenpack.framework.django.mixins import *
from .models import get_image_model
from .decorators import debug_required


class SaveFilesMixin(forms.ModelForm):
    file_or_image_field_name: str = 'files'

    def save(self, commit=True):
        instance = super().save(False)
        if commit:
            instance.save()

            # Обработка загруженных файлов
        uploaded_files = self.cleaned_data.get(self.file_or_image_field_name)
        if uploaded_files:
            saved_files = self.fields[self.file_or_image_field_name].save_files(uploaded_files)
            # Привязываем сохраненные файлы к странице
            for file in saved_files:
                if isinstance(file, get_image_model()):
                    instance.images.add(file)
                else:
                    instance.files.add(file)
            instance.save()

        return instance


class VerboseNameLabelMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Перебираем все поля формы
        for field_name, field in self.fields.items():
            if hasattr(self.Meta, 'labels') and field_name in self.Meta.labels:
                continue
            # Если поле связано с моделью и имеет verbose_name, используем его как label
            try:
                if hasattr(self.Meta, 'model'):
                    model_field = self.Meta.model._meta.get_field(field_name)
                    if hasattr(model_field, 'verbose_name'):
                        field.label = model_field.verbose_name
            except FieldDoesNotExist:
                continue


class RobotOffMixin:
    noindex: bool = True
    nofollow: bool = False

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        headers = list()
        if self.noindex:
            headers.append('noindex')
        if self.nofollow:
            headers.append('nofollow')
        response.headers['X-Robots-Tag'] = ', '.join(headers)
        return response


class DebugRequiredMixin:
    @debug_required
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
