from io import StringIO

import pytest
from django.core.management import call_command


@pytest.fixture
def call_fill_egrul_command():
    out = StringIO()
    call_command('fill_egrul', 'tests/fixtures/', stdout=out)
