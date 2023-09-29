from django.core.management.base import BaseCommand

from ._base_parser import FillOrgParser


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Заполнят БД сведениями из ЕГРЮЛ'

    def add_arguments(self, parser):
        parser.add_argument('dir_name',
                            type=str,
                            help=('Путь до директории,'
                                  ' содержащей сведения из ЕГРЮЛ')
                            )

    def handle(self, *args, **options):
        dir_name = options.get('dir_name')
        parser = FillOrgParser(dir_name)
        orgs, stats = parser.parse_orgs()
        parser.save(orgs)

        for value in stats.values():
            self.stdout.write(
                self.style.SUCCESS(f'{value["verbose_name"]}: {value["value"]}')
            )
