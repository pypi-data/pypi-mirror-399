from typing import Literal
from django.conf import settings
from django.core.management import BaseCommand
from hrenpack.listwork import dict_get
from hrenpack.cmd import is_admin
from hrenpack.system import HostsFile
from .decorators import windows_only


class BaseDNSCommand(BaseCommand):
    action: Literal['add', 'remove']
    hosts_file = HostsFile()

    def add_arguments(self, parser):
        parser.add_argument('-b', '--backup', action='store_true', help="Сделать резервную копию файла hosts")

    @windows_only
    def handle(self, *args, **options):
        if is_admin():
            top_level_domain = dict_get(options, 'top_level_domain', 'com')
            dont_backup = not options['backup']
            project_name = settings.ROOT_URLCONF.split('.')[0]
            domain_name = f'{project_name.lower()}.{top_level_domain}'
            if self.action == 'add':
                self.hosts_file.add_host('127.0.0.1', domain_name, dont_backup)
            else:
                self.hosts_file.remove_host(domain_name, dont_backup)
            print(f"{'Добавление' if self.action == 'add' else 'Удаление'} домена из файла hosts завершено успешно")
        else:
            print("Отказано в доступе")
