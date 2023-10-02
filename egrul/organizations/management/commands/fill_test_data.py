from django.core.management.base import BaseCommand

from ._base_parser import GenerateOrgParser
from ._base_saver import OrgSaver
from ._handlers import Handler


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях с целью демонстрации."""

    help = 'Заполнят БД сведениями для демонстрации'

    def add_arguments(self, parser):
        parser.add_argument('org_num',
                            type=int,
                            help='Количество организаций')

    def handle(self, *args, **options):
        num = options.get('org_num')
        handler = Handler(
            org_parser=GenerateOrgParser(num),
            org_saver=OrgSaver()
        )
        handler.handle()
