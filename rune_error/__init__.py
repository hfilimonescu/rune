from flask import json, render_template, request
from werkzeug.exceptions import HTTPException


__version__ = '0.3.2'


class Error:
    """Rune Error Description"""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Register `Rune_Error` to `app.extensions`
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rune_error'] = self

        # Register `Rune_Error` to `app.rune_apps`
        if not hasattr(app, 'rune_apps'):
            app.rune_apps = {}
        app.rune_apps['rune_error'] = {
            'obj': self,
            'descr': self.__doc__,
            'installable': False,
            'version': __version__,
        }

        from .bp import bp  # noqa

        @bp.app_errorhandler(HTTPException)
        def handle_exception(e):
            """Generic Exception Handlers

            source: https://flask.palletsprojects.com/en/1.1.x/errorhandling/#generic-exception-handlers
            """
            #pylint: disable=unused-variable

            if request.is_json:
                """Return JSON instead of HTML for HTTP errors."""
                response = e.get_response()

                # replace the body with JSON
                response.data = json.dumps({
                    "code": e.code,
                    "name": e.name,
                    "description": e.description,
                })
                response.content_type = "application/json"
                return response
            return render_template('errors/generic_error.html.j2', error=e), 404

        # Modify the blueprint
        # bp.template_folder = 'templates'
        # bp.static_folder = 'static'
        # bp.static_url_path = app.static_url_path + '/error'
        # bp.subdomain = app.config['RUNE_LOCAL_SUBDOMAIN']

        app.register_blueprint(bp)

        app.logger.info('Rune Error started...')
