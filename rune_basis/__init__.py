__version__ = '0.3.2'


class Basis:
    """Rune Basis Description"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        from .bp import bp  # noqa

        from . import admin  # noqa

        # Register `Rune_Basis` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_basis'] = self

        # Register `Rune_Basis` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}

        app.rune_apps['rune_basis'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': True,
            'version': __version__,
        }

        app.register_blueprint(bp)

        app.logger.info('Rune Basis started...')
