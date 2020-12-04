import importlib
import os

from flask import current_app, flash, redirect, render_template, request

from flask_babel import lazy_gettext as _
from flask_login import current_user as cu
from flask_menu import register_menu

from rune.util.url import url_for
from rune_admin.bp import bp
from rune_auth.models import Perm
from rune_auth.decorators import permission_required

from rune_basis.forms import AdminSubmitForm


def _add_permissions(perms=[]):
    for permission in perms:
        if Perm.query.filter_by(name=permission).first() is None:
            p = Perm(name=permission)
            p.update()


def _remove_permissions(perms=[]):
    for name in perms:
        perm = Perm.query.filter_by(name=name).first()
        if perm is not None:
            perm.delete()


def _process_app(app_name=None, action=None):
    if not action:
        current_app.logger.info('No action selected.')
        return

    manage_mod = '.'.join([app_name, 'resources'])

    try:
        mod = importlib.import_module(manage_mod)
    except BaseException:
        current_app.logger.error(
            f'`{app_name}` has no `resources.py`'
        )

    try:
        permissions = getattr(mod, 'PERMS')

        if action == 'install':
            _add_permissions(permissions)
            current_app.logger.warning(
                f'`{app_name}` permissions install ... OK'
            )
        if action == 'uninstall':
            _remove_permissions(permissions)
            current_app.logger.warning(
                f'`{app_name}` permissions remove ... OK'
            )
    except BaseException:
        current_app.logger.error(
            f'`{app_name}` permissions ... NOK'
        )

    try:
        if action == 'install':
            desired_function = getattr(mod, 'run_install')
            current_app.logger.warning(
                f'`{app_name}` other resources install ... OK'
            )
        if action == 'uninstall':
            desired_function = getattr(mod, 'run_remove')
            current_app.logger.warning(
                f'`{app_name}` other resources remove ... OK'
            )

        desired_function()
    except BaseException:
        current_app.logger.error(
            f'`{app_name}` other resources ... NOK'
        )

    return


@bp.route('/basis/')
@register_menu(
    bp,
    '.admin.basis',
    _('Basis'),
    visible_when=lambda: cu.hp('MENU-ADMIN-BASIS'),
    order=99,
    icon='cog',
)
@permission_required('MENU-ADMIN-BASIS')
def basis_main():
    return render_template('admin.base.html.j2')


@bp.route('/basis/apps/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.basis.apps',
    _('Rune Apps'),
    visible_when=lambda: cu.hp('BASIS_ADMIN-LIST'),
    order=10,
    # design='warning',
    icon='cog',
)
@permission_required('BASIS_ADMIN-LIST')
def basis_apps():
    rune_apps = current_app.rune_apps
    form = AdminSubmitForm()

    if not form.validate_on_submit():
        return render_template(
            'basis/admin.apps.list.html.j2',
            rune_apps=rune_apps,
            form=form,
        )

    selected_apps = request.form.getlist('apps')

    # IMPORTANT!
    # First check if the user has the required permissions and then
    # loop through the apps. Otherwise the apps will be un-/installed
    # only partially once the permission for un-/installing has been
    # removed.
    if 'install' in request.form and cu.hp('BASIS_ADMIN-INSTALL'):
        current_app.logger.warning(f'{cu.username} INSTALL {selected_apps}')
        flash('Install process has been started. Check logs for details.',
              'info')
        for app in selected_apps:
            _process_app(app, 'install')

    if 'uninstall' in request.form and cu.hp('BASIS_ADMIN-UNINSTALL'):
        current_app.logger.warning(f'{cu.username} UNINSTALL {selected_apps}')
        flash('Uninstall process has been started. Check logs for details.',
              'info')
        for app in selected_apps:
            _process_app(app, 'uninstall')

    return render_template(
        'basis/admin.apps.list.html.j2',
        rune_apps=rune_apps,
        form=form,
    )


@bp.route('/basis/apps/clean/')
@register_menu(
    bp,
    '.admin.basis.apps.clean',
    _('Clean'),
    visible_when=lambda: False,
    pagemenu=lambda: cu.hp('BASIS_ADMIN-PERMISSIONS-CLEAN'),
    order=10,
    icon='broom',
)
@permission_required('BASIS_ADMIN-PERMISSIONS-CLEAN')
def basis_apps_clean():
    all_apps = current_app.rune_apps
    installable_apps = []
    apps_perms = []
    installed_perms = [perm.name for perm in Perm.query.all()]

    for app in all_apps:
        if all_apps[app]['installable']:
            installable_apps.append(app)

    for app_name in installable_apps:
        manage_mod = '.'.join([app_name, 'resources'])

        try:
            mod = importlib.import_module(manage_mod)
        except BaseException:
            current_app.logger.error(
                f'`{app_name}` has no `resources.py`'
            )

        try:
            permissions = getattr(mod, 'PERMS')

            apps_perms.extend(permissions)
        except BaseException:
            current_app.logger.error(
                f'`{app_name}` permissions ... NOK'
            )

    orphaned_perms = list(set(installed_perms) - set(apps_perms))

    current_app.logger.warning(f'{cu.username} CLEAN {orphaned_perms}')

    for perm in orphaned_perms:
        Perm.query.filter_by(name=perm).first().delete()

    flash(_('Deleted %(count)s orphaned permissions',
            count=len(orphaned_perms)),
          'success')

    return redirect(url_for('admin.basis_apps'))


@bp.route('/basis/versions/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.basis.versions',
    _('Versions'),
    visible_when=lambda: cu.hp('BASIS_ADMIN-LIST'),
    order=80,
    # design='info',
    icon='cog',
)
@permission_required('BASIS_ADMIN-LIST')
def basis_versions():
    form = AdminSubmitForm()

    try:
        import pkg_resources
    except ImportError:
        packages = []

    packages = sorted(pkg_resources.working_set,
                      key=lambda p: p.project_name.lower())

    return render_template(
        'basis/admin.packages.list.html.j2',
        form=form,
        packages=packages,
    )


@bp.route('/basis/menu/', methods=['GET'])
@register_menu(
    bp,
    '.admin.basis.menu',
    _('Menu'),
    visible_when=lambda: cu.hp('BASIS_ADMIN-MENU'),
    order=20,
    # design='info',
    icon='cog',
)
@permission_required('BASIS_ADMIN-MENU')
def basis_menu():
    return render_template(
        'basis/admin.menu.html.j2'
    )
