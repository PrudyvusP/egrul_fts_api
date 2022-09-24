import random
import string

from django.core.management.base import BaseCommand
from mimesis import Generic
from mimesis.builtins import RussiaSpecProvider
from mimesis.locales import Locale

from organizations.models import Organization

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


class Command(BaseCommand):
    """Management-команда для генерации сведений
    об организациях для демонстрации."""

    help = 'Заполнят БД данными для демонстрации'

    def handle(self, *args, **options):
        g = Generic(locale=Locale.RU)
        g.add_provider(RussiaSpecProvider)
        region_code_choices = string.digits
        short_names = list(forms.keys())
        orgs = []
        for _ in range(100000):
            address = (f'{g.address.region().upper()}, '
                       f'{g.address.city().upper()}, '
                       f'{g.address.address().upper()}, '
                       f'{g.address.zip_code()}')
            short_name_abbr = random.choice(short_names)
            full_name_abbr = forms[short_name_abbr]
            word = f'"{g.text.word().upper()}"'
            region_code = (random.choice(region_code_choices)
                           + random.choice(region_code_choices))
            org = Organization(
                inn=g.russia_provider.inn(),
                ogrn=g.russia_provider.ogrn(),
                factual_address=address,
                region_code=region_code,
                short_name=f'{short_name_abbr} {word}',
                full_name=f'{full_name_abbr} {word}'

            )
            orgs.append(org)
        Organization.objects.bulk_create(orgs)
