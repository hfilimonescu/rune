from flask import Flask


__version__ = '0.1.0'


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Rune'

    return app
