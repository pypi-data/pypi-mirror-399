from django.core.files.uploadedfile import UploadedFile
from django.utils.safestring import mark_safe
from hrenpack.framework.django.forms import *
from .models import get_file_model, get_image_model


class UUIDInput(forms.TextInput):
    template_name = 'hrendjango/widgets/UUIDInput.html'

    def __init__(self, attrs=None, uuid_name: str = 'uuid'):
        super(UUIDInput, self).__init__(attrs)
        self.uuid_name = uuid_name

    def get_context(self, name, value, attrs=None):
        context = super(UUIDInput, self).get_context(name, value, attrs)
        context['input__style'] = '''
            text-align: center;
            cursor: pointer;
        '''
        context['name'] = self.uuid_name
        return context


class UUIDField(forms.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', UUIDInput(uuid_name=kwargs.pop('uuid_name')))
        super(UUIDField, self).__init__(*args, **kwargs)


class ClearableFileInput(forms.ClearableFileInput):
    template_name = 'hrendjango/widgets/ClearableFileInput.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['clear__style'] = """
            display: inline-flex;
            align-items: center;
            margin-top: 0;
            margin-left: 40%;
            margin-bottom: 10px;
        """
        return context


class MultipleClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleClearableFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [super().clean(item, initial) for item in data]
        return super().clean(data, initial)


class FileOrImageField(MultipleFileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('file_model', get_file_model())
        kwargs.setdefault('image_model', get_image_model())
        self.FileModel = kwargs.pop('file_model')
        self.ImageModel = kwargs.pop('image_model')
        super().__init__(*args, **kwargs)

    def save(self, data, initial=None):
        # Вызываем родительский метод clean для базовой валидации
        files = self.clean(data, initial)

        # Обрабатываем каждый файл
        saved_files = []
        for file in files:
            if isinstance(file, UploadedFile):
                if file.content_type.startswith('image'):
                    image_file = self.ImageModel(file=file, filename=file.name)
                    image_file.save()
                    saved_files.append(image_file)
                else:
                    other_file = self.FileModel(file=file, filename=file.name)
                    other_file.save()
                    saved_files.append(other_file)

        # Возвращаем список сохраненных файлов
        return saved_files

    def clean(self, data, initial=None):
        files = super().clean(data, initial)
        return files
