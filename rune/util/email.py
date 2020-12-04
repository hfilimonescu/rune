from flask import current_app
from flask_mail import Message

from rune import celery, mail


@celery.task
def send_async_email(subject, recipients, text_body, html_body=None):
    app = current_app._get_current_object()

    subject = app.config.get('RUNE_MAIL_SUBJECT_PREFIX', 'RUNE: ') + subject

    msg = Message(recipients=recipients, subject=subject)
    msg.body = text_body
    msg.html = html_body

    with app.app_context():
        mail.send(msg)
