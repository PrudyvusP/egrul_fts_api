from http import HTTPStatus

import pytest

from utils import TestUtil


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestAPIRetrieve(TestUtil):
    """
    Тестер API метода получения конкретной организации.

    Здесь проверяются:
        HTTP-статусы ответа.
        Структура ответа, типы и значения полей.
        Обработка исключений.
        Идемпотентность GET-методов.
    """

    OK_URL = '/api/organizations/1/'
    BAD_URL = '/api/organizations/2/'
    RESPONSE_RESULT_KEYS = ('full_name', 'short_name', 'inn',
                            'kpp', 'ogrn', 'factual_address', 'region_code')

    def test_01_statuses(self, user_client, organization_1) -> None:
        r = user_client.get(self.OK_URL)
        assert r.status_code == HTTPStatus.OK, self.get_status_text(
            self.OK_URL, r.status_code, HTTPStatus.OK)
        r = user_client.get(self.BAD_URL)
        assert (r.status_code == HTTPStatus.NOT_FOUND), self.get_status_text(
            self.BAD_URL, r.status_code, HTTPStatus.NOT_FOUND)

    def test_02_keys_and_types(self, user_client, organization_1) -> None:
        org = user_client.get(self.OK_URL).data
        assert org, 'Словарь с результатами пустой'
        for response_result_key in self.RESPONSE_RESULT_KEYS:
            assert response_result_key in org, (f'поле '
                                                f'{response_result_key}'
                                                f' отсутствует в ответе')
            condition = isinstance(org[response_result_key], str) is True
            assert condition, (f'типом поля {response_result_key} '
                               f'является {type(org[response_result_key])},'
                               f' а не <str>')

    def test_03_not_found_error(self, user_client) -> None:
        result = user_client.get(self.BAD_URL).data
        assert 'detail' in result, 'Отсутствует ключ detail'
        assert result['detail'] == 'Страница не найдена.', ('Некорректное '
                                                            'сообщение об '
                                                            'ошибке 404')

    def test_04_idempotent(self, user_client, organization_1) -> None:
        r1 = user_client.get(self.OK_URL).data
        r2 = user_client.get(self.OK_URL).data
        assert r1 == r2, 'Система изменила состояние после GET-запросов'

    def test_05_data(self, user_client, organization_1) -> None:
        result = user_client.get(self.OK_URL).data
        assert result['inn'] == organization_1.inn
        assert result['kpp'] == organization_1.kpp
        assert result['ogrn'] == organization_1.ogrn
        assert result['short_name'] == organization_1.short_name
        assert result['full_name'] == organization_1.full_name
        assert result['factual_address'] == organization_1.factual_address
        assert result['region_code'] == organization_1.region_code
