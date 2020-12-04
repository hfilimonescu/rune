from __future__ import absolute_import
import os
from rune import celery, create_app
from celery import Celery, Task
from dotenv import load_dotenv


# To run the worker use the following command
#    `celery -A rune.celery_worker:celery worker -l INFO`


# Load the default config files, just like `flask run` does
load_dotenv('.flaskenv')
load_dotenv('.env')


app = create_app()
app.app_context().push()


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['RESULT_BACKEND'],
        broker=app.config['BROKER_URL'],
        include=[rune_app for rune_app in app.rune_apps])
    celery.conf.update(app.config)

    class ContextTask(Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.test_request_context():
                res = self.run(*args, **kwargs)
                return res

    celery.Task = ContextTask
    celery.config_from_object(__name__)
    celery.conf.timezone = 'UTC'
    return celery


celery = make_celery(app)
