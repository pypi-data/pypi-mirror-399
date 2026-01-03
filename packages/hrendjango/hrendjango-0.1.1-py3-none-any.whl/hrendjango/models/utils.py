from hrendjango.utils import get_model

__all__ = ['get_file_model', 'get_image_model']


def get_file_model():
    return get_model('HRENDJANGO_FILE_MODEL')


def get_image_model():
    return get_model('HRENDJANGO_IMAGE_MODEL')