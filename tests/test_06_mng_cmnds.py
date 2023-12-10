import pytest
from django.core.management import CommandError

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
    TEST_DATA_FILL_COMMAND = 'fill_test_data'

    SUCCESS_MSG = f'Сгенерированных организаций залито: {GENERATE_NUM}\n'
    ARGPARSE_ERROR_MSG = ('Error: argument org_num:'
                          ' Число <org_num> должно быть > 0.')

    def test_01_correct(self, make_call_command):
        make_call_command(self.TEST_DATA_FILL_COMMAND,
                          self.GENERATE_NUM,
                          stdout_message=self.SUCCESS_MSG)

        orgs_query = Organization.objects.all()

        assert orgs_query.count() == self.GENERATE_NUM
        make_call_command(self.TEST_DATA_FILL_COMMAND,
                          self.GENERATE_NUM,
                          stdout_message=self.SUCCESS_MSG)
        assert orgs_query.count() == self.GENERATE_NUM + self.GENERATE_NUM

    def test_02_nonpositive_num(self, make_call_command):
        with pytest.raises(CommandError) as e:
            make_call_command(self.TEST_DATA_FILL_COMMAND,
                              self.NONPOSITIVE_NUM,
                              stdout_message=self.SUCCESS_MSG
                              )
        assert str(e.value) == self.ARGPARSE_ERROR_MSG


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestFillEgrul:
    """
    Здесь проверяются:
    корректное срабатывание команды fill_egrul;
    проверка входных аргументов команде fill_egrul;
    """

    ORG_AND_ITS_UNITS_COUNT = 3
    ORG_AND_ITS_UNITS_OGRN = '2222222222222'

    FILES_COUNT = 1
    ORGS_COUNT = 5
    UPD_ORGS_COUNT = 2
    PROC_NUM = 2

    EGRUL_ARGPARSE_ERROR_PROC_NUM = ('Error: argument -n/--proc-num:'
                                     ' invalid choice:'
                                     ' -4 (choose from 1, 2, 3, 4,'
                                     ' 5, 6, 7, 8)')
    EGRUL_ARGPARSE_ERROR_DIR = ('Error: the following arguments'
                                ' are required: dir_name')

    EGRUL_EMPTY_PATH_DIR = 'tests/fixture/'
    EGRUL_ERROR_MSG = ('Возникла ошибка: Отсутствуют'
                       ' подходящие XML-файлы\n')
    EGRUL_FILL_COMMAND = 'fill_egrul'
    EGRUL_PATH_DIR = 'tests/fixtures/fill'
    EGRUL_SUCCESS_MSG = (f'Обработано файлов: {FILES_COUNT}\n'
                         f'Новых или измененных организаций залито:'
                         f' {ORGS_COUNT}\n')
    EGRUL_SUCCESS_UPD_MSG = (f'Обработано файлов: {FILES_COUNT}\n'
                             f'Новых или измененных организаций залито:'
                             f' {UPD_ORGS_COUNT}\n')
    EGRUL_PATH_UPD_DIR = 'tests/fixtures/update'

    def fill_egrul_ok(self, make_call_command):
        make_call_command(self.EGRUL_FILL_COMMAND, self.EGRUL_PATH_DIR,
                          stdout_message=self.EGRUL_SUCCESS_MSG)

    def test_01_once_filling_and_output(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
        assert Organization.objects.all().count() == self.ORGS_COUNT
        self.fill_egrul_ok(make_call_command)
        assert Organization.objects.all().count() == self.ORGS_COUNT

    def test_02_correct_main(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
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

    def test_03_correct_unit(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
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
                full_name='"ПЕРЕДВИЖНОЙ ЛАЗАРЕТ"'
            )
            .first()
        )
        assert lazaret, 'Организация не найдена в БД'
        assert not lazaret.is_main, 'Организация основная, а не филиал'
        assert lazaret.factual_address == ('КВ-Л. ИЛЬИЧЕВА, Д. 1111, ПГТ.'
                                           ' ЮЖНО-КУРИЛЬСК, САХАЛИНСКАЯ'
                                           ' ОБЛАСТЬ, 694500')
        assert lazaret.ogrn == self.ORG_AND_ITS_UNITS_OGRN

    def test_04_unit_without_address(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
        whale = (
            Organization
            .objects
            .filter(
                full_name='"КИТОВЫЙ ФИЛИАЛ МБУ "СТОПРОЦЕНТНЫЙ ДОМ КУЛЬТУРЫ"'
            )
            .first()
        )
        assert whale, 'Организация не найдена в БД'
        assert whale.ogrn == self.ORG_AND_ITS_UNITS_OGRN
        assert whale.factual_address == 'НЕ УКАЗАН'

    def test_05_unit_without_kpp(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
        shark = (
            Organization
            .objects
            .filter(
                full_name='"АКУЛОВЫЙ ФИЛИАЛ МБУ "СТОПРОЦЕНТНЫЙ ДОМ КУЛЬТУРЫ"'
            )
            .first()
        )
        assert not shark, 'Филиал без КПП попал в БД'

    def test_06_empty_dir(self, make_call_command):
        make_call_command(self.EGRUL_FILL_COMMAND,
                          self.EGRUL_EMPTY_PATH_DIR,
                          stdout_message=self.EGRUL_ERROR_MSG)

    def test_07_proc_num(self, make_call_command):
        make_call_command(self.EGRUL_FILL_COMMAND,
                          self.EGRUL_PATH_DIR,
                          stdout_message=self.EGRUL_SUCCESS_MSG,
                          N=self.PROC_NUM)

    def test_07_proc_num_error(self, make_call_command):
        with pytest.raises(CommandError) as e:
            make_call_command(self.EGRUL_FILL_COMMAND,
                              self.EGRUL_PATH_DIR,
                              '-n=-4',
                              stdout_message=self.EGRUL_SUCCESS_MSG)
        assert str(e.value) == self.EGRUL_ARGPARSE_ERROR_PROC_NUM

    def test_08_no_dir(self, make_call_command):
        with pytest.raises(CommandError) as e:
            make_call_command(self.EGRUL_FILL_COMMAND,
                              stdout_message=self.EGRUL_SUCCESS_MSG)
        assert str(e.value) == self.EGRUL_ARGPARSE_ERROR_DIR

    def test_09_ok_with_update(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
        assert Organization.objects.all().count() == self.ORGS_COUNT
        make_call_command(self.EGRUL_FILL_COMMAND,
                          self.EGRUL_PATH_UPD_DIR,
                          update=True,
                          stdout_message=self.EGRUL_SUCCESS_UPD_MSG,
                          )
        assert Organization.objects.all().count() == self.UPD_ORGS_COUNT

    def test_10_no_liquidated_org(self, make_call_command):
        self.fill_egrul_ok(make_call_command)
        liquidated_org = Organization.objects.filter(
            short_name='ООО "ЛИКВИДИРОВАНО"'
        ).first()
        assert not liquidated_org, 'Ликвидированная организация попала в БД'
