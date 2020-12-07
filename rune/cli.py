import os
from pathlib import Path

import click
from flask import render_template, render_template_string
from flask.cli import with_appcontext
from jinja2 import BaseLoader, Environment


env_string = """RUNE_CONF={{- config.rune_conf }}"""

flaskenv_string = """FLASK_APP=rune.wsgi
FLASK_ENV={{- config.flask_env }}

#FLASK_RUN_EXTRA_FILES={{- config.flask_run_extra_files }}"""

conf_string = """SECRET_KEY = {{ config.secret_key }}


### DebugToolbar Configuration
# Normally not required in production
DEBUG_TB_INTERCEPT_REDIRECTS = False

### SQLAlchemy Configuration
# For MySQL or MariaDB
#SQLALCHEMY_DATABASE_URI = "mysql://<username>:<password>@<ip_or_fqdn>/<db_name>"
# For SQLite3 in a file
SQLALCHEMY_DATABASE_URI = "sqlite:///{{- config.sqlalchemy_database_uri }}"

### Celery Configuration
BROKER_URL = 'pyamqp://'
RESULT_BACKEND = 'redis://localhost'

### Cookies
# A secure cookie has the secure attribute enabled and is only used
# via HTTPS, ensuring that the cookie is always encrypted when
# transmitting from client to server. This makes the cookie less
# likely to be exposed to cookie theft via eavesdropping.
#
# https://github.com/lepture/flask-wtf/issues/76
# SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True
REMEMBER_COOKIE_HTTPONLY = True

RUNE_LOG_STDOUT = False
RUNE_APPS = [
    # ("<module_name>", "<class_name>")
]

RUNE_UI_CARDS_DESIGN = 'light'
RUNE_UI_CARDS_ROW = 5
RUNE_ADMIN_CARDS_ROW = RUNE_UI_CARDS_ROW
RUNE_ADMIN_CARDS_DESIGN = RUNE_UI_CARDS_DESIGN

RUNE_AUTH_LOGIN_FORGOTTEN = False
RUNE_AUTH_LOGIN_REMEMBER = False


RUNE_ADMINS = [
    'rune@example.com',
]
# RUNE_NAME = 'Rune'

# BOOTSTRAP_SERVE_LOCAL = True

### Mail configuration 
# https://pythonhosted.org/Flask-Mail/#configuring-flask-mail
MAIL_SERVER = '<server.fqdn>'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
# MAIL_DEBUG = False
MAIL_USERNAME = '<username>'
MAIL_PASSWORD = '<password>'
# MAIL_DEFAULT_SENDER = (RUNE_NAME, RUNE_ADMINS[0])
# MAIL_MAX_EMAILS = None
# MAIL_SUPPRESS_SEND = True
# MAIL_ASCII_ATTACHMENTS = False"""


@click.group()
def rune():
    """Rune Core commands"""
    pass


@rune.command()
@click.option(
    '-t', '--testing',
    is_flag=True,
    help="Config for testing purposes")
@click.option(
    '-d', '--development',
    is_flag=True,
    help="Config for development purposes")
def init(testing, development):
    """Create the initial env files to run Rune in production"""
    _prefix = ''
    _flask_env = 'production'

    if testing:
        _prefix = 'test_'
        _flask_env = 'testing'

    if development:
        _prefix = 'dev_'
        _flask_env = 'development'

    file_names = [
        (_prefix + 'rune.conf', conf_string),
        ('.env', env_string),
        ('.flaskenv', flaskenv_string),
    ]

    file_paths = [(Path(file), template) for file, template in file_names]

    db_file = _prefix + 'rune.db'
    db_path = Path(db_file)

    config = dict(
        secret_key=os.urandom(24),
        rune_conf=file_paths[0][0].absolute(),
        flask_run_extra_files=':'.join(
            [file for file, template in file_names]),
        flask_env=_flask_env,
        sqlalchemy_database_uri=db_path.absolute(),
    )

    for file, template in file_paths:
        if file.is_file():
            print(
                f'The file `{file}` already exists. Skipping over.')
        else:
            print(f'Write to {file}')
            with open(file, 'w+') as f:
                f.write(
                    Environment(
                        loader=BaseLoader
                    ).from_string(template).render(config=config)
                )


# Worth reading:
# https://flask.palletsprojects.com/en/1.1.x/cli/#custom-scripts
