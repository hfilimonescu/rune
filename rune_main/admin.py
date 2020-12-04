from flask import current_app, flash, redirect, render_template

from flask_babel import lazy_gettext as _
from flask_menu import register_menu
from flask_login import current_user as cu


from rune_admin.bp import bp
from rune_auth.decorators import permission_required
from rune.util.text import b
from rune.util.url import url_for

from .forms import MessageForm
from .models import Notification


@bp.route('/main/message/')
@register_menu(
    bp,
    '.admin.messages',
    _('Messages'),
    order=90,
    visible_when=lambda: cu.hp('MAIN_ADMIN-SYSMSG-LIST'),
    icon='bell')
@permission_required('MAIN_ADMIN-SYSMSG-LIST')
def main_sysmsg_list():
    messages = Notification.query.all()
    # https://stackoverflow.com/a/21338304
    form = MessageForm(locale=cu.locale)

    return render_template('main/admin.message.list.html.j2',
                           messages=messages,
                           form=form,
                           languages=current_app.config.get('OHIE_LANGS'))


@bp.route('/main/message/create/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.messages.create',
    _('Create Message'),
    order=10,
    visible_when=lambda: False,
    icon='plus-square',
    type='primary',
    pagemenu=lambda: cu.hp('MAIN_ADMIN-SYSMSG-CREATE'),
)
@permission_required('MAIN_ADMIN-SYSMSG-CREATE')
def main_sysmsg_create():
    form = MessageForm(locale=cu.locale)

    if form.validate_on_submit():
        message = Notification()
        message.author = cu
        form.populate_obj(message)
        message.update()
        flash(_('Message created successfully.'), 'success')
        return redirect(url_for('admin.main_sysmsg_list'))

    return render_template('main/admin.message.edit.html.j2', form=form)


@bp.route('/main/message/<int:id>/edit/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.messages.edit',
    _('Edit'),
    order=30,
    visible_when=lambda: False,
    icon='pen',
    type='default',
    endpoint_arguments_constructor=lambda: dict(id=1),
    itemmenu=lambda: cu.hp('MAIN_ADMIN-SYSMSG-EDIT'))
@permission_required('MAIN_ADMIN-SYSMSG-EDIT')
def main_sysmsg_edit(id):
    message = Notification.query.get_or_404(id)
    form = MessageForm(obj=message)

    if form.validate_on_submit():
        message.author = cu
        form.populate_obj(message)
        if message.update():
            flash(_('System Message updated sucessfuly'), 'success')
            return redirect(url_for('admin.main_sysmsg_list'))
    return render_template('main/admin.message.edit.html.j2', form=form)


@bp.route('/main/sysmsg/<int:id>/delete/')
@register_menu(
    bp,
    '.admin.messages.delete',
    _('Delete'),
    order=40,
    visible_when=lambda: False,
    icon='trash',
    type='danger',
    endpoint_arguments_constructor=lambda: dict(id=1),
    itemmenu=lambda: cu.hp('MAIN_ADMIN-SYSMSG-DELETE'))
@permission_required('MAIN_ADMIN-SYSMSG-DELETE')
def main_sysmsg_delete(id):
    message = Notification.query.get_or_404(id)
    message.delete()
    return redirect(url_for('admin.main_sysmsg_list'))


@bp.route('/main/message/clean/')
@register_menu(
    bp,
    '.admin.messages.clean',
    _('Clean'),
    order=50,
    visible_when=lambda: False,
    icon='eye-slash',
    type='warning',
    pagemenu=lambda: cu.hp('MAIN_ADMIN-SYSMSG-CLEAN'))
@permission_required('MAIN_ADMIN-SYSMSG-CLEAN')
def main_message_clean():
    messages = Notification.query.all()
    counter = 0
    for message in messages:
        if message.expired:
            counter = counter + 1
            message.delete()
    flash(_('%(counter)s messages have been removed.', counter=b(counter)))
    return redirect(url_for('admin.main_sysmsg_list'))
