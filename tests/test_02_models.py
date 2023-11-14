import datetime

import pytest

from organizations.models import EgrulVersion, Organization


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestOrganizationModel:
    """Здесь проверяются кастомные методы модели Organization."""

    def test_01_str(self, organization_1):
        assert str(organization_1) == ('<МИНИСТЕРСТВО МАГИИ ОГРН'
                                       ' 8888888888888, 7777777777/999999999>')

    def test_02_truncate_ri(self, organization_1, organization_2):
        orgs_before = Organization.objects.all()
        assert orgs_before
        Organization.truncate_ri()
        orgs_after = Organization.objects.all()
        assert not orgs_after


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestEgrulVersionModel:
    """Здесь проверяются кастомные методы модели EgrulVersion."""

    def test_01_str(self, organization_1):
        version = EgrulVersion.objects.first()
        assert str(version) == f'<Версия от {datetime.date.today()}>'
