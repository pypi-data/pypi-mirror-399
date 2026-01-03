from typing import Optional
from .mixins import DebugRequiredMixin


class BaseDebug(DebugRequiredMixin):
    do_method_name: Optional[str] = None

    def do(self, *args, **kwargs):
        if self.do_method_name is not None:
            eval(f'self.{self.do_method_name}(*args, **kwargs)')
        else:
            raise ValueError(f'do_method_name not defined')

