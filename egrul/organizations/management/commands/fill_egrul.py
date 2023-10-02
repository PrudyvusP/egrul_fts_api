from django.core.management.base import BaseCommand

from organizations.models import Organization
from ._base_parser import XMLOrgParser
from ._base_saver import OrgSaver
from ._handlers import Handler


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
        Organization.truncate_ri()
        dir_name = options.get('dir_name')
        handler = Handler(
            org_parser=XMLOrgParser(dir_name, update=False),
            org_saver=OrgSaver()
        )
        handler.handle()
