import click
from flask.cli import with_appcontext


@click.group()
def auth():
    """Rune A12n and A11n commands"""
    pass


@auth.command()
@with_appcontext
def create_ddic():
    """Create the DDIC user"""
    print('Creating user DDIC...')

    from rune import db  # noqa
    from rune_auth.models import User  # noqa

    ddic = User()
    ddic.username = 'ddic'
    ddic.name = 'Dedicated User'
    ddic.email = 'ddic@rhhr.ro'
    ddic.password = 'RUNE'
    ddic.locale = 'en'
    db.session.add(ddic)
    db.session.commit()

    print('Created user DDIC.')
