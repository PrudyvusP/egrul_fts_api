import pytest
from rest_framework.test import APIClient

from organizations.management.commands._parsers import GenerateOrgParser
from organizations.models import Organization


@pytest.fixture
def user_client():
    return APIClient()


@pytest.fixture
def organization_1():
    return Organization.objects.create(
        full_name='МИНИСТЕРСТВО МАГИИ',
        short_name='МИНИСТЕРСТВО МАГИИ',
        inn='1' * 11,
        ogrn='1' * 12,
        kpp='1' * 9,
        factual_address='УЛ. ВОЛШЕБНИКОВ, Г. МОСКВА, 125212',
        region_code='77'
    )

@pytest.fixture
def many_organizations():
    parser = GenerateOrgParser(num=21)
    orgs, _, __ = parser.parse()
    return Organization.objects.bulk_create(orgs)
