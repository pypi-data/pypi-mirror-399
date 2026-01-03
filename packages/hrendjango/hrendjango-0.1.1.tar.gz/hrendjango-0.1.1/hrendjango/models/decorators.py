import os
from django.db import models

__all__ = ['delete_files_on_delete']


def delete_files_on_delete(cls):
    """Декоратор класса для удаления файлов при удалении записи"""
    original_delete = cls.delete

    def new_delete(self, *args, **kwargs):
        for field in self._meta.get_fields():
            if isinstance(field, (models.FileField, models.ImageField)):
                file = getattr(self, field.name)
                if file and os.path.isfile(file.path):
                    os.remove(file.path)
        original_delete(self, *args, **kwargs)

    cls.delete = new_delete
    return cls
