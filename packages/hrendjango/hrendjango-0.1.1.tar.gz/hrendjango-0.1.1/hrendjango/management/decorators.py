import platform


def windows_only(func):
    def wrapper(self, *args, **options):
        if platform.system() == 'Windows':
            return func(self, *args, **options)
        print("Данная функция работает только на Windows")
    return wrapper
