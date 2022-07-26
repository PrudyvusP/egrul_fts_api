import os
import xml.etree.cElementTree as ElTree

from django.core.management.base import BaseCommand

from organizations.utils import (Organization, get_organization_object,
                                 get_organization_ogrn)


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Заполнят БД сведениями из ЕГРЮЛ'

    def add_arguments(self, parser):
        parser.add_argument('dir_names',
                            nargs='+',
                            type=str,
                            help=('Путь(-и) до директории,'
                                  ' содержащие сведения из ЕГРЮЛ')
                            )

        parser.add_argument('-u',
                            '--update',
                            action='store_true',
                            help='Create an admin account')

    def handle(self, *args, **options):

        organizations = []
        counter = 0
        counter_norm = 0
        counter_likv = 0
        counter_update = 0
        update_flag = options['update']

        for dir_name in options['dir_names']:
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.stdout.write(
                        self.style.WARNING(
                            f'работаю с файлом {file_path}'
                        )
                    )
                    counter += 1
                    tree = ElTree.parse(file_path)
                    elements = tree.findall('СвЮЛ')
                    for element in elements:
                        if not element.find('СвПрекрЮЛ'):
                            counter_norm += 1
                            org = get_organization_object(element)
                            organizations.append(org)
                        else:
                            counter_likv += 1
                            if update_flag:
                                counter_update += 1
                                ogrn = get_organization_ogrn(element)
                                try:
                                    org = Organization.objects.get(ogrn=ogrn)
                                    org.delete()
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f'Орг-ия с ОГРН {ogrn} удалена'
                                        )
                                    )
                                except Organization.DoesNotExist:
                                    self.stdout.write(
                                        self.style.ERROR(
                                            (f'Орг-ии с ОГРН {ogrn}'
                                             f' не существует')
                                        )
                                    )

            Organization.objects.bulk_create(organizations)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Действующих организаций залито: {counter_norm}.\n'
                    f'Ликвидированных организаций {counter_likv}.\n'
                    f'Обработано файлов {counter}.'
                )
            )
