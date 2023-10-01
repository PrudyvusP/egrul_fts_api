import datetime
import os
import random
import string

from django.core.exceptions import ObjectDoesNotExist
from lxml import etree as ElTree
from mimesis import Generic
from mimesis.builtins import RussiaSpecProvider
from mimesis.locales import Locale

from organizations.models import Organization, EgrulVersion
from ._private import get_organization_objects, get_organization_ogrn

BATCH_SIZE = 10000

forms = {
    "ПАО": "ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО",
    "ОАО": "ОТКРЫТОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО",
    "АО": "АКЦИОНЕРНОЕ ОБЩЕСТВО",
    "ГУП": "ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ",
    "БУЗ": "БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ ЗДРАВООХРАНЕНИЯ",
    "АКБ": "АКЦИОНЕРНЫЙ КОММЕРЧЕСКИЙ БАНК",
    "ГК": "ГАРАЖНЫЙ КООПЕРАТИВ",
    "ООО": "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ",
    "НПО": "НАУЧНО-ПРОИЗВОДСТВЕННЫЙ КОМПЛЕКС",
    "ФКУ": "ФЕДЕРАЛЬНОЕ КАЗЕНОЕ УЧРЕЖДЕНИЕ"
}


class OrgParser:

    def parse_orgs(self):
        pass

    def save(self, orgs):
        Organization.objects.bulk_create(orgs, batch_size=BATCH_SIZE)
        try:
            version = EgrulVersion.objects.get(pk=1)
            version.version = datetime.date.today()
            version.save()
        except ObjectDoesNotExist:
            EgrulVersion.objects.create(id=1, version=datetime.date.today())


class FillOrgParser(OrgParser):

    def __init__(self, dir_name):
        self.dir_name = dir_name

    def parse_orgs(self):
        """Возвращает список действующих организаций
        из XML-файлов ЕГРЮЛ."""

        orgs = []
        counter = 0
        counter_liq = 0
        counter_new = 0

        for root, dirs, files in os.walk(self.dir_name):
            for file in files:
                file_path = os.path.join(root, file)
                counter += 1
                tree = ElTree.parse(file_path)
                elements = tree.findall('СвЮЛ')

                for element in elements:
                    if element.find('СвПрекрЮЛ'):
                        counter_liq += 1
                    else:
                        orgs_from_xml = get_organization_objects(element)
                        counter_new += len(orgs_from_xml)
                        orgs.extend(orgs_from_xml)

        stats = {
            'counter': {
                "verbose_name": 'Обработано файлов',
                "value": counter
            },
            'counter_liq': {
                "verbose_name": 'Ликвидированных организаций пропущено',
                "value": counter_liq
            },
            'counter_new': {
                "verbose_name": 'Действующих организаций залито',
                "value": counter_new
            },
        }
        return orgs, stats


class UpdateOrgParser(OrgParser):

    def __init__(self, dir_name):
        self.dir_name = dir_name

    def parse_orgs(self):
        """Возвращает список действующих организаций из XML-файлов ЕГРЮЛ:
        1) если организация действующая и не присутствует в БД, то добавляет
        организацию и ее филиалы в список;
        2) если организация есть в БД, но прекратила свое действие,
        то удаляет организацию и ее филиалы из БД;
        3) если организация есть в БД и действующая, то удаляет
         организацию и ее филиалы из БД и добавляет ее организацию и филиалы
         в список."""

        orgs = []
        counter = 0
        counter_new = 0
        counter_liq = 0
        counter_upd = 0

        for root, dirs, files in os.walk(self.dir_name):
            for file in files:
                file_path = os.path.join(root, file)
                counter += 1
                tree = ElTree.parse(file_path)
                elements = tree.findall('СвЮЛ')

                for element in elements:
                    ogrn = get_organization_ogrn(element)
                    orgs_from_db = Organization.objects.filter(ogrn=ogrn)

                    # TODO кажется, логика сбоит

                    if orgs_from_db:

                        if element.find('СвПрекрЮЛ'):
                            counter_liq += len(orgs_from_db)
                        else:
                            orgs_from_xml = get_organization_objects(element)
                            counter_upd += len(orgs_from_xml)
                            orgs.extend(orgs_from_xml)
                        # TODO есть подозрение, что это грязь (нагрузка на БД)
                        orgs_from_db.delete()
                    else:
                        orgs_from_xml = get_organization_objects(element)
                        counter_new += len(orgs_from_xml)
                        orgs.extend(orgs_from_xml)

        stats = {
            'counter': {
                "verbose_name": 'Обработано файлов',
                "value": counter
            },
            'counter_liq': {
                "verbose_name": 'Ликвидированных организаций пропущено',
                "value": counter_liq
            },
            'counter_new': {
                "verbose_name": 'Действующих организаций залито',
                "value": counter_new
            },
            'counter_upd': {
                "verbose_name": 'Изменений в организации внесено:',
                "value": counter_upd
            }
        }

        return orgs, stats


class TestOrgParser(OrgParser):

    def __init__(self, num):
        self.num = num

    def parse_orgs(self):
        g = Generic(locale=Locale.RU)
        g.add_provider(RussiaSpecProvider)
        region_code_choices = string.digits
        short_names = list(forms.keys())
        orgs = []
        for _ in range(self.num):
            address = (f'{g.address.address().upper()}, '
                       f'{g.address.city().upper()}, '
                       f'{g.address.region().upper()}, '
                       f'{g.address.zip_code()}')
            short_name_abbr = random.choice(short_names)
            full_name_abbr = forms[short_name_abbr]
            word = f'"{g.text.word().upper()}"'
            region_code = (random.choice(region_code_choices)
                           + random.choice(region_code_choices))
            org = Organization(
                inn=g.russia_provider.inn(),
                ogrn=g.russia_provider.ogrn(),
                kpp=g.russia_provider.kpp(),
                factual_address=address,
                region_code=region_code,
                short_name=f'{short_name_abbr} {word}',
                full_name=f'{full_name_abbr} {word}'

            )
            orgs.append(org)

        stats = {
            'counter_new': {
                "verbose_name": 'Действующих организаций залито',
                "value": self.num
            }
        }
        return orgs, stats
