from flask import render_template

from flask_babel import lazy_gettext as _
from flask_login import current_user as cu
from flask_menu import register_menu

from rune_auth.decorators import permission_required

from .bp import bp


@bp.route('/')
@register_menu(
    bp,
    '.admin',
    _('Admin'),
    icon='tools',
    order=90,
    visible_when=lambda: cu.hp('MENU-ADMIN'),
)
@permission_required('MENU-ADMIN')
def main():
    """This will show cards of all RUNE Apps that have registered menus
    under the `admin` entry point."""
    return render_template('admin.base.html.j2')
