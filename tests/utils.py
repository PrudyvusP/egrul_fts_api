class TestUtil:

    @staticmethod
    def get_status_text(url: str,
                        cur_status_code: int,
                        expected_status_code: int) -> str:
        return (f'{url} возвращает {cur_status_code}'
                f' вместо {expected_status_code}')
