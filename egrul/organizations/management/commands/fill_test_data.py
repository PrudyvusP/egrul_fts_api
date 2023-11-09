from argparse import ArgumentTypeError

from django.core.management.base import BaseCommand

from ._handlers import TestDataHandler


def positive(numeric_type):
    def require_positive(value):
        number = numeric_type(value)
        if number < 0:
            raise ArgumentTypeError("Число <org_num> должно быть > 0.")
        return number

    return require_positive


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях с целью демонстрации."""

    help = 'Заполнят БД сведениями для демонстрации'

    def add_arguments(self, parser):
        parser.add_argument('org_num',
                            type=positive(int),
                            help='Количество организаций')

    def handle(self, *args, **options):
        handler = TestDataHandler(num=options.get('org_num'))
        stats = handler.handle()
        for stat in stats:
            self.stdout.write(f'{stat}: {stats[stat]}')
