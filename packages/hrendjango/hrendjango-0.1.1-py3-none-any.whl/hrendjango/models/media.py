from .base import AbstractFile, AbstractImageFile

__all__ = ['MediaFile', 'ImageMediaFile']


class MediaFile(AbstractFile):
    class Meta(AbstractFile.Meta):
        abstract = False
        swappable = 'HRENDJANGO_FILE_MODEL'


class ImageMediaFile(AbstractImageFile):
    class Meta(AbstractImageFile.Meta):
        abstract = False
        swappable = 'HRENDJANGO_IMAGE_MODEL'
