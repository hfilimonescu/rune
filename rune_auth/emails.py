from flask import render_template
from flask_babel import gettext as _


from rune.util.email import send_async_email


def user_new(user, password):
    send_async_email.delay(
        subject=_('Your New Account'),
        recipients=[user.email],
        text_body=render_template('auth/email.user_new.txt.j2',
                                  password=password, user=user),
        html_body=render_template('auth/email.user_new.html.j2',
                                  password=password, user=user)
    )


def user_change_email(user, old_email, new_email):
    send_async_email.delay(
        subject=_('Email for %(name)s has changed.', name=user.name),
        recipients=[old_email, new_email],
        text_body=render_template('auth/email.user_change_email.txt.j2',
                                  user=user,
                                  old_email=old_email,
                                  new_email=new_email),
        html_body=render_template('auth/email.user_change_email.html.j2',
                                  user=user,
                                  old_email=old_email,
                                  new_email=new_email)
    )


def user_reset_password(user, password):
    send_async_email.delay(
        subject=_('Password Reset'),
        recipients=[user.email],
        text_body=render_template('auth/email.user_reset_password.txt.j2',
                                  user=user,
                                  password=password),
        html_body=render_template('auth/email.user_reset_password.html.j2',
                                  user=user,
                                  password=password)
    )
