from django.core.management.base import BaseCommand

from ._handlers import TestDataHandler


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях с целью демонстрации."""

    help = 'Заполнят БД сведениями для демонстрации'

    def add_arguments(self, parser):
        parser.add_argument('org_num',
                            type=int,
                            help='Количество организаций')

    def handle(self, *args, **options):
        handler = TestDataHandler(num=options.get('org_num'))
        handler.handle()
