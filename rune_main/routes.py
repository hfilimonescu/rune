from flask import render_template

from flask_babel import lazy_gettext as _
from flask_menu import register_menu


from .bp import bp
from .models import Notification


@bp.route('/')
@register_menu(bp, '.main', _('Messages'), order=0, icon='inbox',
               visible_when=lambda: False)
def index():
    messages = Notification.read()
    return render_template('main/routes.index.html.j2', messages=messages)


@bp.route('/about')
@register_menu(bp, '.about', _('About Rune'), order=0, visible_when=lambda: False)
def about():
    return render_template('main/routes.about.html.j2')
