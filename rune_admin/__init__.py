__version__ = '0.3.2'


class Admin:
    """Rune Admin Package"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app=None):
        # Set default config parameters
        app.config.setdefault('RUNE_ADMIN_CARDS_ROW', 4)
        app.config.setdefault('RUNE_ADMIN_CARDS_DESIGN', 'light')

        from . import routes  # noqa

        # Register `RUNE_Admin` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_admin'] = self

        # Register `RUNE_Admin` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}
        app.rune_apps['rune_admin'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': True,
            'version': __version__,
        }

        # Register blueprint
        from .bp import bp  # noqa
        app.register_blueprint(bp)

        app.logger.info('Rune Admin started...')
