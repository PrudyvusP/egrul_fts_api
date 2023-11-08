import datetime
from http import HTTPStatus

import pytest

from utils import TestUtil


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestAPIList(TestUtil):
    """
    Тестер API метода получения списка организаций.

    Здесь проверяются:
        HTTP-статусы ответа.
        Структура ответа, типы и значения полей.
        Пагинация.
        Поиск.
        Идемпотентность GET-методов.
    """

    URL = '/api/organizations/'
    RESPONSE_KEYS = ('count', 'next', 'previous', 'date_info', 'results')
    RESPONSE_RESULT_KEYS = ('full_name', 'short_name', 'inn',
                            'kpp', 'relative_addr')
    INN_SEARCH_PARAM = {"search": "7777777777"}
    OGRN_SEARCH_PARAM = {"search": "8888888888888"}
    KPP_SEARCH_PARAM = {"search": "999999999"}

    def test_01_statuses(self, user_client) -> None:
        status = user_client.get(self.URL).status_code
        assert status == HTTPStatus.OK, self.get_status_text(
            self.URL, status, HTTPStatus.OK)

    def test_02_main_keys(self, user_client) -> None:
        data = user_client.get(self.URL).data
        for response_key in self.RESPONSE_KEYS:
            assert response_key in data, (f'поле {response_key}'
                                          f' отсутствует в ответе')

    def test_03_main_types_wo_pagination(
            self, user_client, organization_1) -> None:
        data = user_client.get(self.URL).data

        assert isinstance(data['count'], int), ('значение поля count '
                                                'не является <int>')
        assert isinstance(data['results'], list), ('значение поля results'
                                                   ' не является списком')
        assert isinstance(data['date_info'], datetime.date), ('значение '
                                                              'поля date_info'
                                                              'не является'
                                                              '<datetime.date>'
                                                              )

    def test_04_result_keys_and_types(
            self, user_client, organization_1) -> None:
        organizations = user_client.get(self.URL).data['results']
        assert organizations, 'список организаций пустой'
        org = organizations[0]
        for response_result_key in self.RESPONSE_RESULT_KEYS:
            assert response_result_key in org, (f'поле'
                                                f' {response_result_key} '
                                                f'отсутствует в ответе')

            condition = isinstance(org[response_result_key], str) is True
            assert condition, (f'типом поля {response_result_key} '
                               f'является {type(org[response_result_key])},'
                               f' а не <str> ')

    def test_05_pagination_keys_types(self, user_client,
                                      organization_1,
                                      organization_2,
                                      reset_page_size) -> None:
        result = user_client.get(self.URL).data
        assert result['count'] == 2, 'Неожиданное число организаций'
        next_page = result['next']
        prev_page = result['previous']
        assert next_page, 'Отсутствует ссылка на след. страницу'
        assert isinstance(next_page, str), f'Вместо <str> {type(next_page)}'
        assert not prev_page, 'Появилась лишняя ссылка на пред. страницу'
        result2 = user_client.get(next_page).data
        assert result2['count'] == 2, 'Неожиданное число организаций'
        next_page2 = result2['next']
        prev_page2 = result2['previous']
        assert not next_page2, 'Появилась лишняя ссылка на след. страницу'
        assert prev_page2, 'Отсутствует ссылка на пред. страницу'
        assert isinstance(prev_page2, str), f'Вместо <str> {type(prev_page2)}'

    def test_06_search(self, user_client, organization_1) -> None:
        by_inn = user_client.get(self.URL, data=self.INN_SEARCH_PARAM).data
        by_kpp = user_client.get(self.URL, data=self.KPP_SEARCH_PARAM).data
        by_ogrn = user_client.get(self.URL, data=self.OGRN_SEARCH_PARAM).data
        assert by_inn['results']
        assert by_kpp['results']
        assert by_ogrn['results']
        assert by_inn['results'][0]['full_name'] == 'МИНИСТЕРСТВО МАГИИ'
        assert by_kpp['results'][0]['full_name'] == 'МИНИСТЕРСТВО МАГИИ'
        assert by_ogrn['results'][0]['full_name'] == 'МИНИСТЕРСТВО МАГИИ'

    def test_07_idempotent(self, user_client,
                           organization_1, organization_2) -> None:
        r1 = user_client.get(self.URL).data
        r2 = user_client.get(self.URL).data
        assert r1 == r2, 'Система изменила состояние после GET-запросов'

    def test_08_data(self, user_client, organization_1) -> None:
        orgs = user_client.get(self.URL).data['results']
        assert orgs, 'Список организаций пустой'
        org = orgs[0]
        assert org['inn'] == organization_1.inn
        assert org['kpp'] == organization_1.kpp
        assert org['short_name'] == organization_1.short_name
        assert org['full_name'] == organization_1.full_name
        assert org['relative_addr'] == '/api/organizations/1/'
