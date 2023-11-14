class TestProjectSettings:
    """Здесь проверяются настройки приложения."""

    def test_debug_off(self, settings):
        assert not settings.DEBUG, 'DEBUG-режим нужно выключить!'
