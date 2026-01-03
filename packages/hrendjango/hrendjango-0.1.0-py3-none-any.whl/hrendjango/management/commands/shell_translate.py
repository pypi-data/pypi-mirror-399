from django.core.management.base import BaseCommand
from django.utils.translation import gettext


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            print(gettext(input(gettext("Enter the expression to translate") + ':\n')))
