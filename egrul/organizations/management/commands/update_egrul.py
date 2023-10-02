from django.core.management.base import BaseCommand

from ._base_deleter import OrgDeleter
from ._base_parser import XMLOrgParser
from ._base_saver import OrgSaver
from ._handlers import Handler


class Command(BaseCommand):
    """Management-команда для внесения изменений
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Вносит в БД изменения из ЕГРЮЛ'

    def add_arguments(self, parser):
        parser.add_argument('dir_name',
                            type=str,
                            help=('Путь до директории,'
                                  ' содержащей сведения из ЕГРЮЛ')
                            )

    def handle(self, *args, **options):
        dir_name = options.get('dir_name')
        handler = Handler(
            org_parser=XMLOrgParser(dir_name, update=True),
            org_saver=OrgSaver(),
            org_deleter=OrgDeleter()
        )
        handler.handle()
