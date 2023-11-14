from http import HTTPStatus

import pytest

from utils import TestUtil


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestAPIFTSSearch(TestUtil):
    """
    Тестер API метода полнотекстового поиска.
    Полностью совпадает с тестами списка организаций
    за исключением поиска по ИНН, КПП, ОГРН.

    Здесь проверяются:
        HTTP-статусы ответа.
        Реализация полнотекстового поиска.
    """

    URL = '/api/organizations/fts-search/'
    QUERY_PARAM = {"q": "магия"}
    RESPONSE_KEYS = ('count', 'next', 'previous', 'date_info', 'results')
    RESPONSE_RESULT_KEYS = ('full_name', 'short_name', 'inn',
                            'kpp', 'relative_addr')

    def test_01_statuses(self, user_client) -> None:
        r = user_client.get(self.URL)
        assert r.status_code == HTTPStatus.BAD_REQUEST, self.get_status_text(
            self.URL, r.status_code, HTTPStatus.BAD_REQUEST)
        r = user_client.get(self.URL, data=self.QUERY_PARAM)
        assert r.status_code == HTTPStatus.OK, self.get_status_text(
            self.URL, r.status_code, HTTPStatus.OK)

    def test_02_bad_request_error(self, user_client) -> None:
        result = user_client.get(self.URL).data
        assert 'detail' in result, 'Отсутствует ключ detail'
        assert (result['detail']
                == 'Необходимо передать параметр q'), ('Некорректное '
                                                       'сообщение об '
                                                       'ошибке 400')

    def test_03_fts(self, user_client, organization_1, organization_2) -> None:
        result = user_client.get(self.URL, data=self.QUERY_PARAM).data
        orgs = result['results']
        assert len(orgs) == 1, 'Полнотекстовый поиск вернул странный результат'
        org = orgs[0]
        assert org['full_name'] == 'МИНИСТЕРСТВО МАГИИ', ('Полное наименование'
                                                          ' не совпадает'
                                                          ' с ожидаемым')
        assert org['inn'] == '7777777777', 'ИНН не совпадает с ожидаемым'
