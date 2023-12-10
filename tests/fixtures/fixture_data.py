import datetime

import pytest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.test import APIClient

from organizations.models import EgrulVersion, Organization


def fill_egrul_version():
    try:
        version = EgrulVersion.objects.get(pk=1)
        version.version = datetime.date.today()
        version.save()
    except ObjectDoesNotExist:
        EgrulVersion.objects.create(id=1, version=datetime.date.today())


@pytest.fixture
def user_client():
    return APIClient()


@pytest.fixture
def organization_1():
    fill_egrul_version()
    return Organization.objects.create(
        full_name='МИНИСТЕРСТВО МАГИИ',
        short_name='МИНИСТЕРСТВО МАГИИ',
        inn='7777777777',
        ogrn='8888888888888',
        kpp='999999999',
        factual_address='УЛ. ВОЛШЕБНИКОВ, Г. МОСКВА, 125212',
        region_code='77'
    )


@pytest.fixture
def organization_2():
    fill_egrul_version()
    return Organization.objects.create(
        full_name='АКЦИОНЕРНОЕ ОБЩЕСТВО "ТЕСТЫ ЗДЕСЬ"',
        short_name='АО "ТЕСТЫ ЗДЕСЬ"',
        inn='1111111111',
        ogrn='7777777777777',
        kpp='666666666',
        factual_address='УЛ. ТЕСТЕРОВ, Г. ТЕСТОВ, 212125',
        region_code='02'
    )


@pytest.fixture
def unit_of_organization_1():
    fill_egrul_version()
    return Organization.objects.create(
        full_name='МИНИСТЕРСТВО МАГИИ РЕСПУБЛИКИ ЧУВАШИИ',
        short_name='МИНИСТЕРСТВО МАГИИ РЕСПУБЛИКИ ЧУВАШИИ',
        inn='7777777777',
        ogrn='8888888888888',
        kpp='111111111',
        factual_address='УЛ. ВОИНОВ-ИНТЕРНАЦИОНАЛТИСТОВ, Г. НОВОЧЕБОКСАРСК, '
                        'Д.34, 111111',
        region_code='21',
        is_main=False
    )
