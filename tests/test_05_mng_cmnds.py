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
    корректное срабатывание команды fill_egrul;
    проверка входных аргументов команде fill_egrul;
    """

    COMMAND_NAME = 'fill_egrul'
    PATH_WITH_XML = 'tests/fixtures/'
    FILES_COUNT = 1
    ORGS_COUNT = 5
    ORG_AND_ITS_UNITS_COUNT = 3
    ORG_AND_ITS_UNITS_OGRN = '2222222222222'

    def test_01_once_filling_and_output(self, call_fill_egrul_command):
        assert Organization.objects.all().count() == self.ORGS_COUNT

        out = StringIO()
        call_command(self.COMMAND_NAME, self.PATH_WITH_XML, stdout=out)
        assert (out.getvalue()
                == (f'Обработано файлов: {self.FILES_COUNT}\n'
                    f'Новых или измененных организаций залито:'
                    f' {self.ORGS_COUNT}\n')
                )

        call_command(self.COMMAND_NAME, self.PATH_WITH_XML, stdout=out)
        assert (Organization.objects.all().count()
                != self.ORGS_COUNT + self.ORGS_COUNT)

    def test_02_correct_main(self, call_fill_egrul_command):
        chudesa = (
            Organization
            .objects
            .filter(inn=2222222222, kpp=333333333, ogrn=1111111111111)
            .first()
        )
        assert chudesa
        assert chudesa.full_name == ('ОБЩЕСТВО С ОГРАНИЧЕННОЙ '
                                     'ОТВЕТСТВЕННОСТЬЮ "КОМПАНИЯ "ЧУДЕСА"')
        assert chudesa.short_name == 'ООО "КОМПАНИЯ ЧУДЕСА"'
        assert chudesa.factual_address == ('ПР-КТ. ЛЕНИНА, Д. 00А,'
                                           ' Г. ОКТЯБРЬСКИЙ, РЕСПУБЛИКА'
                                           ' БАШКОРТОСТАН, 452613')
        assert chudesa.region_code == '02'

    def test_03_correct_unit(self, call_fill_egrul_command):
        org_with_unit = (
            Organization
            .objects
            .filter(ogrn=self.ORG_AND_ITS_UNITS_OGRN)
            .all()
        )
        assert org_with_unit.count() == self.ORG_AND_ITS_UNITS_COUNT
        lazaret = (
            Organization
            .objects
            .filter(
                full_name=('МУНИЦИПАЛЬНОЕ БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ "СТОПРОЦЕНТНЫЙ'
                           ' ДОМ КУЛЬТУРЫ". "ПЕРЕДВИЖНОЙ ЛАЗАРЕТ"')
            )
            .first()
        )
        assert lazaret
        assert lazaret.factual_address == ('КВ-Л. ИЛЬИЧЕВА, Д. 1111, ПГТ.'
                                           ' ЮЖНО-КУРИЛЬСК, САХАЛИНСКАЯ'
                                           ' ОБЛАСТЬ, 694500')
        assert lazaret.ogrn == self.ORG_AND_ITS_UNITS_OGRN

    def test_04_unit_without_address(self, call_fill_egrul_command):
        whale = (
            Organization
            .objects
            .filter(
                full_name=('МУНИЦИПАЛЬНОЕ БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ'
                           ' "СТОПРОЦЕНТНЫЙ ДОМ КУЛЬТУРЫ".'
                           ' "КИТОВЫЙ ФИЛИАЛ МБУ "СТОПРОЦЕНТНЫЙ ДОМ КУЛЬТУРЫ"')
            )
            .first()
        )
        assert whale
        assert whale.ogrn == self.ORG_AND_ITS_UNITS_OGRN
        assert whale.factual_address == 'НЕ УКАЗАН'

    def test_05_unit_without_kpp(self, call_fill_egrul_command):
        shark = (
            Organization
            .objects
            .filter(
                full_name=('МУНИЦИПАЛЬНОЕ БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ'
                           ' "СТОПРОЦЕНТНЫЙ ДОМ КУЛЬТУРЫ".'
                           ' "АКУЛОВЫЙ ФИЛИАЛ МБУ "СТОПРОЦЕНТНЫЙ'
                           ' ДОМ КУЛЬТУРЫ"')
            )
            .first()
        )
        assert not shark

    def test_06_empty_dir(self):
        pass

    def test_07_proc_num(self):
        pass
