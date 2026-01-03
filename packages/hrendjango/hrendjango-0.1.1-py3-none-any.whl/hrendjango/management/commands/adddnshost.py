from hrendjango.management.base import BaseDNSCommand


class Command(BaseDNSCommand):
    action = 'add'
    help = "Добавляет название проекта в файл hosts"

    def add_arguments(self, parser):
        parser.add_argument('top_level_domain', type=str, help="Домен верхнего уровня", nargs='?', default=None)
        super().add_arguments(parser)
