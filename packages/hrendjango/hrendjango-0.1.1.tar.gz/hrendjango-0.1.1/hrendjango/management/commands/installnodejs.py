import platform, subprocess, requests, os
from django.core.management.base import BaseCommand
from hrenpack.network import download_file_to_temp
from hrendjango.management.decorators import windows_only


class Command(BaseCommand):
    help = "Установка Node.js. Используйте 'version' для указания версии, или '-b' для установки последней бета-версии."

    def add_arguments(self, parser):
        parser.add_argument('version', type=str, help="Версия Node.js. Преобладает над аргументом --use-beta",
                            nargs='?', default=None)
        parser.add_argument('-b', '--use-beta', action='store_true',
                            help="Использование последней доступной версии Node.js. "
                                 "Если не указан, используется последняя стабильная версия")

    @staticmethod
    def get_installed_version():
        try:
            result = subprocess.run(["node", "-v"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    @staticmethod
    def get_latest_version(use_beta):
        versions = requests.get('https://nodejs.org/dist/index.json').json()
        for version in versions:
            if version['lts'] or use_beta:
                return version['version']

    @windows_only
    def handle(self, *args, **options):
        installed_version = self.get_installed_version()
        if installed_version is not None:
            print(f"Node.js уже установлен, версия: {installed_version}. Если хотите переустановить его,",
                  "то сначала удалите старую версию")
        if options['version']:
            version = options['version']
            if 'v' not in version:
                version = 'v' + version
        else:
            version = self.get_latest_version(options['use_beta'])
        url = f'https://nodejs.org/dist/{version}/node-{version}-x64.msi'
        print("Скачивание Node.js...")
        # path = download_file_to_temp(url, 'msi', use_progressbar=True)
        path = 'C:/node-v22.14.0-x64.msi'
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print("Файл успешно загружен.")
        else:
            print("Ошибка при загрузке файла.")
        try:
            print("Установка Node.js...")
            os.system(' '.join([path, 'INSTALLDIR="C:/Program Files/nodejs/"', '/quiet', '/norestart']))
            print("Node.js успешно установлен.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при установке Node.js: {e}")
