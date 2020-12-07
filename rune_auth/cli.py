import click
from flask import current_app
from flask.cli import with_appcontext


@click.group()
def auth():
    """Rune A12n and A11n commands"""
    pass


@auth.command()
@with_appcontext
def create_admins():
    """Create the dedicated user"""
    from rune import db  # noqa
    from rune_auth.models import User  # noqa

    admin_list = current_app.config.get('RUNE_ADMINS')

    for admin in admin_list:
        username = admin.split('@')[0]
        if User.query.filter_by(email=admin).first():
            click.secho(f'User {admin} already exists...', fg='yellow')
        else:
            click.secho(f'Creating user {admin}...', fg='cyan')
            auser = User()
            auser.email = admin
            auser.username = username
            auser.password = 'RUNE'
            auser.name = username
            auser.locale = 'en'
            auser.force_pwd_change = True
            db.session.add(auser)
            click.secho(f'Created user {admin}.', fg='green')

    db.session.commit()
