from flask import flash, request
from flask_babel import lazy_gettext as _
from flask_login import LoginManager, current_user, logout_user


login = LoginManager()

login.login_view = 'auth.login'
login.login_message_category = 'info'

__version__ = '0.3.2'


class Auth:
    """Core application of Rune to manage users, authentication,
    and authorization."""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Set default configuration
        app.config.setdefault('RUNE_AUTH_LOGIN_REMEMBER', True)
        app.config.setdefault('RUNE_AUTH_LOGIN_FORGOTTEN', True)

        from .bp import bp  # noqa

        from . import admin  # noqa
        from . import routes  # noqa

        login.init_app(app)

        @app.before_request
        def before_request():
            """Logout all users who have been deactivated after
            their login. This applies to all requests to the app,
            not for the blueprint. """
            #pylint: disable=unused-argument

            if current_user.is_authenticated and not current_user.active:
                flash(_('Your account is not active!'), 'error')
                logout_user()

        # Register `Rune_Auth` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_auth'] = self

        # Register `Rune_Auth` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}
        app.rune_apps['rune_auth'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': True,
            'version': __version__,
        }

        app.register_blueprint(bp)

        app.logger.info('Rune Auth started...')
