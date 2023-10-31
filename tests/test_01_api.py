from http import HTTPStatus

import pytest


@pytest.mark.django_db(transaction=True)
class TestOrganizationAPI:
    ORGANIZATION_URL = '/api/organizations/'
    RESPONSE_KEYS = ('count', 'next', 'previous', 'date_info', 'results')
    RESPONSE_RESULT_KEYS = ('full_name', 'short_name', 'inn',
                            'kpp', 'relative_addr')

    def test_01_organizations_url_ok(self, user_client) -> None:
        r = user_client.get(self.ORGANIZATION_URL)
        stat_code = r.status_code
        assert stat_code == HTTPStatus.OK, (f'{self.ORGANIZATION_URL}'
                                            f' возвращает'
                                            f' {stat_code} вместо 200')

    def test_02_organizations_response_keys(self, user_client) -> None:
        r = user_client.get(self.ORGANIZATION_URL)

    def test_03_organization_response_keys_and_types(
            self, user_client, many_organizations) -> None:
        r = user_client.get(self.ORGANIZATION_URL)
        data = r.data
        for response_key in self.RESPONSE_KEYS:
            assert response_key in data, (f'поле {response_key}'
                                          f' отсутствует в ответе')
        assert isinstance(data['count'], int)
        assert isinstance(data['next'], str)
        assert isinstance(data['results'], list), ('значение поля results'
                                                   ' не является списком')
        print(r.data)
        assert 1 == 1

    def test_04_organizations_response_result_keys_and_types(
            self, user_client, organization_1) -> None:
        r = user_client.get(self.ORGANIZATION_URL)
        organizations = r.data['results']
        assert organizations, 'список организаций пустой'
        org = organizations[0]
        for response_result_key in self.RESPONSE_RESULT_KEYS:
            assert response_result_key in org, (f'поле'
                                                f' {response_result_key} '
                                                f'отсутствует в ответе')

            condition = isinstance(org[response_result_key], str) is True
            assert condition, (f'типом поля {response_result_key} '
                               f'является {type(org[response_result_key])},'
                               f' а не строка (str)')
