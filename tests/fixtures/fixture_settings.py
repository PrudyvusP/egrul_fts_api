import pytest


@pytest.fixture
def reset_page_size(settings):
    page = settings.REST_FRAMEWORK['PAGE_SIZE']
    settings.REST_FRAMEWORK['PAGE_SIZE'] = 1
    yield
    settings.REST_FRAMEWORK['PAGE_SIZE'] = page
