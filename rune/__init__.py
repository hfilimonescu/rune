import importlib
import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from celery import Celery
from flask import Flask, g, session, request
from flask_babel import Babel
from flask_bs4 import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import current_user as cu
from flask_mail import Mail
from flask_menu import Menu
from flask_migrate import Migrate
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy

from rune_admin import Admin
from rune_auth import Auth
from rune_basis import Basis
from rune_error import Error
from rune_main import Main
from rune_theme import Theme

from sqlalchemy import MetaData

from .config import Config

__version__ = '0.3.2'


# https://stackoverflow.com/a/46785675
# https://github.com/miguelgrinberg/Flask-Migrate/issues/61#issuecomment-208131722
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


babel = Babel()
bootstrap = Bootstrap()
celery = Celery(__name__)
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
mail = Mail()
menu = Menu()
migrate = Migrate()
moment = Moment()
pagedown = PageDown()
toolbar = DebugToolbarExtension()


rune_admin = Admin()
rune_auth = Auth()
rune_basis = Basis()
rune_error = Error()
rune_main = Main()
rune_theme = Theme()


@babel.localeselector
def get_locale():
    if session.get('locale'):
        return session['locale']
    # return cu.locale or request.accept_languages.best_match(
    #     [lang[0] for lang in Config.RUNE_LANGUAGES])
    if cu.is_authenticated and cu.locale is not None:
        session['locale'] = cu.locale
        return cu.locale
    else:
        # Returns the first tuple element from a list of tuples
        guess = request.accept_languages.best_match(
            [lang[0] for lang in Config.RUNE_LANGUAGES])
        session['locale'] = guess
        return guess


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load default config of the project
    app.config.from_object(Config)

    if test_config is None:
        app.config.from_envvar('RUNE_CONF', silent=True)
    else:
        app.config.update(test_config)

    # Make sure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Celery initialization
    celery.conf.update(app.config)

    # Check if the db is sqlite. Needed by `render_as_batch` in
    # `migrate.init_app`
    is_sqlite = app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite://')

    @app.before_request
    def before_request():
        g.locale = get_locale()

    # Create `app.rune_apps`
    if not hasattr(app, 'rune_apps'):
        app.rune_apps = {}

    # Init Flask extensions
    babel.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    menu.init_app(app)
    migrate.init_app(app, db, render_as_batch=is_sqlite)
    moment.init_app(app)
    pagedown.init_app(app)
    toolbar.init_app(app)

    # Worth reading about logging
    # https://flask.palletsprojects.com/en/1.1.x/quickstart/#logging
    if app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['RUNE_ADMINS'],
                subject='{} Failure'.format(app.config['RUNE_NAME']),
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['RUNE_LOG_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(stream_handler)
        else:
            # Define the log details
            log_path = os.path.join(app.instance_path, 'log')
            log_file = app.config['RUNE_NAME'] + '.log'

            # Ensure the log folder exists
            try:
                os.makedirs(log_path)
            except OSError:
                pass

            file_handler = RotatingFileHandler(
                os.path.join(log_path, log_file),
                maxBytes=10240,
                backupCount=20)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[%(pathname)s: %(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

    # Init Rune applications
    # IMPORTANT: The order in whitch you initialize them matters

    # `auth` needs to be on top so its model can be referenced by other apps.
    rune_auth.init_app(app)

    # Automatically load the applications listed in the config file
    for pkg_name, pkg_class in app.config.get('RUNE_APPS', []):
        if pkg_name not in app.rune_apps:
            pkg_instance = importlib.import_module(pkg_name)
            pkg_object = getattr(pkg_instance, pkg_class)
            pkg_object(app)

    rune_error.init_app(app)
    rune_basis.init_app(app)
    rune_main.init_app(app)

    # Keep this order, so that other blueprints register the routes
    # before `admin` is initialized.
    rune_admin.init_app(app)
    rune_theme.init_app(app)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Rune started...')

    return app
