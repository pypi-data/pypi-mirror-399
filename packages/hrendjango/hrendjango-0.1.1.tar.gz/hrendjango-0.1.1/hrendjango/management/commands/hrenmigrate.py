import os, glob
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from hrenpack.date_and_time_work import now_to_str
from hrenpack.filework import TextFile
from hrendjango import __version__


class Command(BaseCommand):
    help = 'Creates a migration for the specified app and optionally runs it'
    app_label = 'hrendjango'
    migration_directory = os.path.join(settings.BASE_DIR, app_label, "migrations")
    file = None

    def add_arguments(self, parser):
        parser.add_argument('-m', '--migrate', action='store_true', help='Run the migration after creating it')

    def get_last_migration_filename(self):
        try:
            migration_files = glob.glob(os.path.join(self.migration_directory, '*.py'))
            migration_files = [f for f in migration_files if not f.endswith('__init__.py')]
            latest_migration = max(migration_files, key=os.path.getctime)
            return os.path.basename(latest_migration)
        except ValueError:
            return None

    def handle(self, *args, **options):
        migrate = options['migrate']
        latest_migration_filename = self.get_last_migration_filename()
        call_command('makemigrations', self.app_label)
        new_migration_filename = self.get_last_migration_filename()
        if latest_migration_filename != new_migration_filename:
            self.change_file(new_migration_filename)
        if migrate:
            call_command('migrate', self.app_label)

    def change_file(self, migration_name):
        self.file = TextFile(os.path.join(self.migration_directory, migration_name))
        split = '\n\nclass Migration(migrations.Migration):\n'
        pre_class_text, class_text = self.file.read().split(split)
        pre_class_text = (f'# Сгенерировано HrenDjango версии {__version__} {now_to_str()}\n' +
                          '\n'.join(pre_class_text.split('\n')[1:]))
        if 'migrations.CreateModel' in class_text:
            pre_class_text += 'from hrendjango.utils import create_model\n'
        pre_class_text += 'from hrenpack.listwork import del_none\n\n\n'
        class_text = split + class_text
        class_text = class_text.replace('operations = [', 'operations = del_none(')
        class_text = class_text.replace('migrations.CreateModel', 'create_model')
        class_text = class_text[:-2] + ')\n'
        self.file.rewrite(pre_class_text + class_text[2:])
