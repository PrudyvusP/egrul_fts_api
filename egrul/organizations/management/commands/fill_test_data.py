from django.core.management.base import BaseCommand

from ._base_parser import TestOrgParser


class Command(BaseCommand):
    """Management-команда для генерации сведений
    об организациях для демонстрации."""

    help = 'Заполнят БД сведениями для демонстрации'

    def add_arguments(self, parser):
        parser.add_argument("org_num", type=int)

    def handle(self, *args, **options):
        num = options.get("org_num")
        parser = TestOrgParser(num)
        orgs, stats = parser.parse_orgs()
        parser.save(orgs)

        for value in stats.values():
            self.stdout.write(
                self.style.SUCCESS(f'{value["verbose_name"]}: {value["value"]}')
            )
