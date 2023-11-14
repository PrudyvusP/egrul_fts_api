from django.core.management.base import BaseCommand

from ._handlers import EgrulHandler


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Заполнят БД сведениями из ЕГРЮЛ'

    def add_arguments(self, parser):
        parser.add_argument('dir_name',
                            type=str,
                            help=('Путь до директории,'
                                  ' содержащей XML-файлы ЕГРЮЛ')
                            )
        parser.add_argument('-n', '--proc-num',
                            type=int,
                            dest='N',
                            choices=range(1, 9),
                            metavar="[1-8]",
                            default=1,
                            help=('Количество процессов [1-8]'
                                  ' (по умолчанию: 1)')
                            )
        parser.add_argument('--update',
                            dest='is_update',
                            action='store_true',
                            help=('Флаг переключения режимов.'
                                  ' Если включён, то режим обновления')
                            )

    def handle(self, *args, **options):
        handler = EgrulHandler(
            cpu_count=options.get('N'),
            dir_name=options.get('dir_name'),
            is_update=options.get('is_update')
        )
        stats = handler.handle()
        for stat in stats:
            self.stdout.write(f'{stat}: {stats[stat]}')
