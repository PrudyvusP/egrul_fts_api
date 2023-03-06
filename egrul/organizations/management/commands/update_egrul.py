import os
import xml.etree.cElementTree as ElTree

from django.core.management.base import BaseCommand

from ._private import get_organization_objects, get_organization_ogrn
from organizations.models import Organization


class Command(BaseCommand):
    """Management-команда для внесения изменений
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Вносит в БД изменения из ЕГРЮЛ'

    def add_arguments(self, parser):
        parser.add_argument('dir_names',
                            nargs='+',
                            type=str,
                            help=('Путь(-и) до директории,'
                                  ' содержащие сведения из ЕГРЮЛ')
                            )

    def handle(self, *args, **options):

        organizations = []
        counter = 0
        counter_new = 0
        counter_liq = 0
        counter_upd = 0

        for dir_name in options['dir_names']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Начинаю работать с {dir_name}'
                )
            )
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    file_path = os.path.join(root, file)
                    counter += 1
                    tree = ElTree.parse(file_path)
                    elements = tree.findall('СвЮЛ')
                    for element in elements:
                        ogrn = get_organization_ogrn(element)
                        orgs_from_db = Organization.objects.filter(ogrn=ogrn)
                        if orgs_from_db:
                            if element.find('СвПрекрЮЛ'):
                                counter_liq += len(orgs_from_db)
                            else:
                                orgs = get_organization_objects(element)
                                counter_upd += len(orgs)
                                organizations.extend(orgs)
                            orgs_from_db.delete()
                        else:
                            orgs = get_organization_objects(element)
                            counter_new += len(orgs)
                            organizations.extend(orgs)
                self.stdout.write(
                    self.style.WARNING(
                        f'Обработано файлов: {counter}'
                    )
                )
                Organization.objects.bulk_create(organizations)
                organizations.clear()
        self.stdout.write(
            self.style.SUCCESS(
                f'Новых организаций залито: {counter_new}.\n'
                f'Ликвидированных организаций удалено: {counter_liq}.\n'
                f'Изменений в организации внесено: {counter_upd}.'
            )
        )
