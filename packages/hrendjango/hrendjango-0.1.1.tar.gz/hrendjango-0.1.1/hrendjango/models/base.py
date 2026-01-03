import uuid
from django.db import models
from .mixins import DeleteFilesMixin

__all__ = ['AbstractFile', 'AbstractImageFile']


class AbstractFile(DeleteFilesMixin, models.Model):
    file = models.FileField(upload_to='files/', verbose_name="Файл")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Уникальный идентификатор")
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_update = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    filename = models.CharField(max_length=255, verbose_name="Имя файла")

    class Meta:
        abstract = True
        verbose_name = "файл"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.filename


class AbstractImageFile(AbstractFile):
    file = models.ImageField(upload_to='images/', verbose_name="Изображение")

    class Meta:
        abstract = True
        verbose_name = "изображение"
        verbose_name_plural = "Изображения"
