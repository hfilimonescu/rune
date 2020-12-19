from flask import Blueprint


__version__ = '0.3.2'


class Theme:
    """Rune Theme Description"""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('RUNE_UI_THEME', 'theme')
        app.config.setdefault('RUNE_MAIN_VIEW', 'main.index')

        app.config.setdefault('RUNE_LOCAL_SUBDOMAIN', None)
        app.config.setdefault('RUNE_THEME_ALERT_AUTOCLOSE', 5000)

        app.config.setdefault('MOMENT_DEFAULT_FORMAT', 'L')

        blueprint = Blueprint(
            'theme',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/theme',
            subdomain=app.config['RUNE_LOCAL_SUBDOMAIN']
        )

        # Register `RUNE_Theme` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_theme'] = self

        # Register `RUNE_Theme` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}
        app.rune_apps['rune_theme'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': False,
            'version': __version__,
        }

        app.register_blueprint(blueprint)

        app.logger.info('Rune Theme started...')
