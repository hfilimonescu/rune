import pytest


class TestRune:
    """Rune"""

    def test_app_extensions(self, app):
        """`app.extensions` is a `dict`"""
        assert isinstance(app.extensions, dict)

    def test_rune_apps(self, app):
        """`app.rune_apps` is a `dict`"""

        assert isinstance(app.rune_apps, dict)

    def test_rune_apps_list(self, app):
        """All core apps are registered in `app.rune_apps`"""

        current_list = list(app.rune_apps)
        expected_list = [
            'rune_admin',
            'rune_auth',
            'rune_basis',
            'rune_error',
            'rune_main',
            'rune_theme',
        ]

        for app in expected_list:
            assert app in current_list

    def test_blueprints(self, app):
        expected_blueprints = [
            'admin',
            'auth',
            'basis',
            'bootstrap',
            'errors',
            'main',
            'theme',
        ]

        assert isinstance(app.blueprints, dict)
        print(list(app.blueprints))
        for blueprint in expected_blueprints:
            assert blueprint in list(app.blueprints)

    def test_default_config(self, app):
        """Default config values"""
        rune_langs = app.config.get('RUNE_LANGUAGES')

        assert app.config.get('BABEL_DOMAIN') == 'rune'
        assert app.config.get('RUNE_NAME') == 'Rune'
        assert app.config.get('RUNE_MAIL_SUBJECT_PREFIX') == 'Rune: '
        assert app.config.get('RUNE_DEFAULT_LOCALE') == 'de'

        assert app.config.get('RUNE_UI_APP_LOGO')
        assert not app.config.get('RUNE_LOG_STDOUT')

        assert isinstance(app.config.get('RUNE_APPS'), list)
        assert isinstance(app.config.get('RUNE_ADMINS'), list)
        assert isinstance(rune_langs, list)
        assert ('en', 'English') in rune_langs
        assert ('de', 'Deutsch') in rune_langs
        assert ('ro', 'Română') in rune_langs
