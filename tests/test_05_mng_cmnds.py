from io import StringIO

import pytest
from django.core.management import call_command, CommandError

from organizations.models import Organization


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestFillTestData:
    """
    Здесь проверяются:
    корректное срабатывание команды fill_test_data;
    передача неположительного числа на вход команде fill_test_data.
    """

    GENERATE_NUM = 2
    NONPOSITIVE_NUM = -1

    def test_01_correct(self):
        out = StringIO()
        call_command('fill_test_data', self.GENERATE_NUM, stdout=out)
        assert (out.getvalue()
                == (f'Сгенерированных организаций '
                    f'залито: {self.GENERATE_NUM}\n'))
        orgs_query = Organization.objects.all()

        assert orgs_query.count() == self.GENERATE_NUM
        call_command('fill_test_data', self.GENERATE_NUM, stdout=out)
        assert orgs_query.count() == self.GENERATE_NUM + self.GENERATE_NUM

    def test_02_nonpositive_num(self):
        with pytest.raises(CommandError) as e:
            call_command('fill_test_data', self.NONPOSITIVE_NUM)
        assert str(e.value) == ('Error: argument org_num:'
                                ' Число <org_num> должно быть > 0.')


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestFillEgrul:
    """
    Здесь проверяются:
    корректное срабатывание команда fill_egrul;
    проверка входных аргументов команде fill_egrul;
    """

    def test_01_correct(self):
        pass
