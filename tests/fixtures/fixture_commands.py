from io import StringIO

import pytest
from django.core.management import call_command, CommandError


@pytest.fixture
def make_call_command():
    def _make_call_command(command, *args, **kwargs):
        message = kwargs.pop('stdout_message')
        out = StringIO()
        call_command(command, *args, stdout=out, **kwargs)
        assert out.getvalue() == message

    return _make_call_command


@pytest.fixture
def call_fill_test_data_non_pos_arg():
    with pytest.raises(CommandError) as e:
        call_command('fill_test_data', -1)
    assert str(e.value) == ('Error: argument org_num:'
                            ' Число <org_num> должно быть > 0.')
