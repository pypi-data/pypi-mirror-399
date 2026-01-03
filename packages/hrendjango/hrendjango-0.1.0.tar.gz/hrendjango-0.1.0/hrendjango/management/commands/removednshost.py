from hrendjango.management.base import BaseDNSCommand


class Command(BaseDNSCommand):
    action = 'remove'
    help = "Удаляет название проекта из файла hosts"
