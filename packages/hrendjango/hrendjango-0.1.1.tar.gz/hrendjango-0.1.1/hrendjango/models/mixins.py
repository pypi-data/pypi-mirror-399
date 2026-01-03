import os
from django.db import models
from django.core.files.storage import default_storage

__all__ = ['DeleteFilesMixin']


class DeleteFilesMixin:
    """Миксин для гарантированного удаления файлов при удалении модели"""

    def delete(self, *args, **kwargs):
        # Получаем полную информацию о файлах ДО удаления модели
        files_info = self._collect_files_info()

        # Удаляем модель (включая все связанные объекты)
        result = super().delete(*args, **kwargs)

        # Удаляем файлы после успешного удаления модели
        self._delete_collected_files(files_info)
        return result

    def _collect_files_info(self):
        """Собирает информацию о всех файлах модели"""
        files_info = []
        for field in self._meta.get_fields():
            if isinstance(field, (models.FileField, models.ImageField)):
                file = getattr(self, field.name)
                if file:
                    files_info.append({
                        'field': field.name,
                        'file': file,
                        'path': file.path if hasattr(file, 'path') else None,
                        'name': file.name,
                        'storage': file.storage
                    })
        return files_info

    def _delete_collected_files(self, files_info):
        """Удаляет собранные файлы с обработкой всех исключений"""
        for info in files_info:
            try:
                storage = info['storage']
                name = info['name']

                # Удаляем основной файл
                if storage.exists(name):
                    storage.delete(name)

                # Для ImageField удаляем все вариации (thumbnails)
                if hasattr(info['file'], 'field') and isinstance(info['file'].field, models.ImageField):
                    self._delete_image_variations(info)
            except Exception as e:
                print(f"Failed to delete file {name}: {str(e)}")

    def _delete_image_variations(self, file_info):
        """Удаляет вариации изображений (для ImageField)"""
        try:
            field = file_info['file'].field
            if hasattr(field, 'variations'):
                for variation in field.variations:
                    variation_name = file_info['file'].field.get_variation_name(
                        file_info['name'], variation
                    )
                    if file_info['storage'].exists(variation_name):
                        file_info['storage'].delete(variation_name)
        except Exception as e:
            print(f"Failed to delete image variations: {str(e)}")

    @classmethod
    def register_signals(cls):
        """Регистрирует сигналы для обработки bulk/cascade удаления"""
        from django.db.models.signals import pre_delete
        from django.dispatch import receiver

        @receiver(pre_delete, sender=cls)
        def handle_pre_delete(sender, instance, **kwargs):
            if isinstance(instance, DeleteFilesMixin):
                files_info = instance._collect_files_info()
                instance._delete_collected_files(files_info)
