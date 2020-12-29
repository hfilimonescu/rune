__version__ = '0.3.3.dev'


class API:
    """Rune API Description"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Register `rune_api` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_api'] = self

        # Register `rune_api` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}

        app.rune_apps['rune_api'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': False,
            'version': __version__,
        }

        from .bp import bp  # noqa

        app.register_blueprint(bp)

        app.logger.info('Rune API started...')
