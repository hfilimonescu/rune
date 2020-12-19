__version__ = '0.3.2'


class Main:
    """Rune Main Description"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('RUNE_MAIN_VIEW', 'main.index')

        from flask_login import login_required  # noqa

        from .bp import bp  # noqa
        bp.static_url_path = app.static_url_path + '/main'

        @bp.before_request
        @login_required
        def before_request():
            #pylint: disable=unused-argument
            pass

        from . import admin  # noqa
        from . import routes  # noqa

        # Register `RUNE_Main` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_main'] = self

        # Register `RUNE_Main` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}
        app.rune_apps['rune_main'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': True,
            "version": __version__,
        }

        app.register_blueprint(bp)

        app.logger.info('Rune Main started...')
