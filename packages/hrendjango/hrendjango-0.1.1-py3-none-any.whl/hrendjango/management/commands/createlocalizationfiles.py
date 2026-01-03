import os
from datetime import datetime
from pathlib import Path
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from hrenpack.classes import TransposedList
from hrenpack.listwork import dict_get
from hrendjango.constants import LANGS_PLURALIZE


class Command(BaseCommand):
    help = 'Генерирует PO-файлы для указанного приложения и языков'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='Название приложения')
        parser.add_argument('langs', nargs='*', type=str, help='Коды языков')
        parser.add_argument('--exclude-date', '-d', action='store_true',
                            help='Исключить даты из заголовков PO-файлов')
        parser.add_argument('--all-langs', '-a', action='store_true', help="Использовать все языки, поддерживаемые Django")

    def handle(self, *args, **options):
        app_name = options['app_name']
        date = str(datetime.now())[:16]
        exclude_date = options['exclude_date']
        verbose = options['verbosity'] > 1
        langs = options['langs'] if not options['all_langs'] else list(LANGS_PLURALIZE)
        langs = TransposedList(settings.LANGUAGES)[0] if not langs else langs

        if verbose:
            self.stdout.write(f"Начало генерации PO для приложения: {app_name}")
            self.stdout.write(f"Языки: {langs}")

        try:
            app_config = apps.get_app_config(app_name)
            app_dir = app_config.path
            if verbose:
                self.stdout.write(f"Приложение найдено в: {app_dir}")
        except LookupError:
            self.stderr.write(f'Приложение "{app_name}" не найдено')
            return

        po_props_dict = {
            "Project-Id-Version": app_name,
            "POT-Creation-Date": date,
            "PO-Revision-Date": date,
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=UTF-8",
            "Content-Transfer-Encoding": "8bit",
        }

        for lang in langs:
            if lang not in LANGS_PLURALIZE:
                self.stderr.write(f'Язык "{lang}" не поддерживается, пропускаем')
                continue

            if verbose:
                self.stdout.write(f"\nОбработка языка: {lang}")

            # Подготовка заголовков PO
            po_text = 'msgid ""\nmsgstr ""\n'
            dct = po_props_dict.copy()
            dct.update({
                'Language': lang,
                'Plural-Forms': LANGS_PLURALIZE[lang]
            })

            if exclude_date:
                dct.pop('POT-Creation-Date', None)
                dct.pop('PO-Revision-Date', None)

            for key, value in dct.items():
                po_text += f'"{key}: {value}\\n"\n'

            # Создание директории, если её нет
            po_dir = Path(app_dir) / 'locale' / lang / 'LC_MESSAGES'
            if verbose:
                self.stdout.write(f"Целевая директория: {po_dir}")

            try:
                po_dir.mkdir(parents=True, exist_ok=True)
                if verbose:
                    self.stdout.write(f"Директория создана/существует: {po_dir.exists()}")
            except Exception as e:
                self.stderr.write(f'Ошибка создания директории {po_dir}: {e}')
                continue

            po_file = po_dir / 'django.po'
            if verbose:
                self.stdout.write(f"Попытка записи в: {po_file}")

            try:
                with po_file.open('w', encoding='utf-8') as file:
                    file.write(po_text)
                self.stdout.write(f'Файл {po_file} успешно создан')
            except IOError as e:
                self.stderr.write(f'Ошибка записи в файл {po_file}: {e}')
                # Вывод полного пути для отладки
                self.stderr.write(f'Полный путь: {po_file.absolute()}')
