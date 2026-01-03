from typing import Union
from django.urls.converters import StringConverter


class BaseLiteralStringConverter(StringConverter):
    allowed: Union[list, tuple, set]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.allowed:
            raise ValueError("Список разрешенных значений пуст")
        self.regex = '|'.join(self.allowed)

    def to_python(self, value):
        if value not in self.allowed:
            raise ValueError(f"Недопустимое значение. Допустимые: {self.allowed}")
        return value

    def to_url(self, value):
        if value not in self.allowed:
            raise ValueError(f"Недопустимое значение для URL. Допустимые: {self.allowed}")
        return value
