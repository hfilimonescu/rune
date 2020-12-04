from flask import current_app, flash, redirect, render_template, request

from flask_babel import lazy_gettext as _
from flask_login import current_user as cu
from flask_menu import register_menu

from rune.util.text import b
from rune.util.url import url_for
from rune_auth.decorators import permission_required
from rune_auth.emails import user_change_email, user_new
from rune_auth.forms import (AdminRoleCreateForm, AdminRoleForm,
                             AdminUserCreateForm, AdminUserEditForm,
                             AdminUserRoleForm)
from rune_auth.models import Perm, Role, User
from rune_auth.password import password_generator

from rune_admin.bp import bp


@bp.route('/auth/')
@register_menu(
    bp,
    '.admin.auth',
    _('Authentication'),
    visible_when=lambda: cu.hp('MENU-ADMIN-AUTH'),
    order=10,
    icon='lock')
@permission_required('MENU-ADMIN-AUTH')
def auth_main():
    return render_template('admin.base.html.j2')


@bp.route('/auth/user/')
@register_menu(
    bp,
    '.admin.auth.user',
    _('Users'),
    visible_when=lambda: cu.hp('AUTH_ADMIN-USER-LIST'),
    order=10,
    icon='users')
@permission_required('AUTH_ADMIN-USER-LIST')
def auth_user_list():
    userlist = User.query.all()
    form = AdminUserCreateForm()

    return render_template(
        'auth/admin.user.list_old.html.j2',
        userlist=userlist,
        form=form,
    )


@bp.route('/auth/user/create/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.auth.user.create',
    _('Create User'),
    order=10,
    type='primary',
    icon='user-plus',
    visible_when=lambda: False,
    pagemenu=lambda: cu.hp('AUTH_ADMIN-USER-CREATE'),
)
@permission_required('AUTH_ADMIN-USER-CREATE')
def auth_user_create():
    form = AdminUserCreateForm()

    if form.validate_on_submit():
        password = password_generator()

        user = User()
        form.populate_obj(user)

        user.password = password
        user.confirmed = True
        user.force_pwd_change = True

        if user.update():
            user_new(user, password)
            flash(_('User %(name)s has been created.', name=b(user.name)),
                  'success')
            return redirect(url_for('admin.auth_user_list'))

    return render_template('auth/admin.user.edit.html.j2', form=form)


@bp.route('/auth/user/<username>/')
@register_menu(
    bp,
    '.admin.auth.user.read',
    _('View'),
    order=20,
    type='light',
    icon='eye',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(username='user'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-USER-READ'))
@permission_required('AUTH_ADMIN-USER-READ')
def auth_user_read(username):
    user = User.query.filter_by(username=username).first()

    return render_template(
        'auth/admin.user.read.html.j2',
        user=user,
    )


@bp.route('/auth/user/<username>/edit/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.auth.user.edit',
    _('Edit'),
    order=30,
    type='light',
    icon='pen',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(username='user'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-USER-EDIT'))
@permission_required('AUTH_ADMIN-USER-EDIT')
def auth_user_edit(username):
    user = User.query.filter_by(username=username).first()
    if user._is_ddic:
        flash(_('You are not allowed to edit the DDIC user.'), 'error')
        return redirect(url_for('admin.auth_user_list'))
    if user is None:
        flash(_('Username and Email for %(username)s already modified.',
                username=b(username)), 'error')
        return redirect(url_for('admin.auth_user_list'))

    form = AdminUserEditForm(obj=user)

    if form.validate_on_submit():
        if user.email != form.email.data:
            user_change_email(user, user.email, form.email.data)

        form.populate_obj(user)

        user.update()

        flash(_('User %(name)s has been updated.', name=b(user.name)),
              'success')

        return redirect(url_for('admin.auth_user_list'))

    return render_template(
        'auth/admin.user.edit.html.j2',
        form=form,
        user=user,
    )


@bp.route('/auth/user/<username>/roles/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.auth.user.roles',
    _('Roles'),
    order=50,
    type='light',
    icon='boxes',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(username='user'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-USER-ROLES'))
@permission_required('AUTH_ADMIN-USER-ROLES')
def auth_user_roles(username):
    user = User.query.filter_by(username=username).first()
    if user._is_ddic:
        flash(_('You are not allowed to edit the DDIC user.'), 'error')
        return redirect(url_for('admin.auth_user_list'))

    available_roles = Role.query.all()
    form = AdminUserRoleForm()

    if form.validate_on_submit():
        selected_roles = request.form.getlist('roles')
        user.update_roles(available_roles, selected_roles)
        flash(_('Roles for %(name)s have been updated.',
                name=b(user.name)), 'success')
        return redirect(url_for('admin.auth_user_list'))

    return render_template(
        'auth/admin.user.roles.html.j2',
        form=form,
        user=user,
        roles=available_roles)


@bp.route('/auth/user/<username>/delete/')
@register_menu(
    bp,
    '.admin.auth.user.delete',
    _('Delete'),
    order=40,
    type='light',
    icon='trash',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(username='user'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-USER-DELETE'))
@permission_required('AUTH_ADMIN-USER-DELETE')
def auth_user_delete(username):
    if cu.username == username:
        flash(_('You are not allowed to delete your own user!'), 'danger')
        return redirect(url_for('admin.auth_user_list'))

    user = User.query.filter_by(username=username).first()

    if user._is_ddic:
        flash(_('You are not allowed to edit the DDIC user.'), 'error')
        return redirect(url_for('admin.auth_user_list'))

    if user is None:
        current_app.logger.error(
            '%s failed to delete %s',
            cu.username,
            username)
        flash(_('User %(username)s does not exist.',
                username=b(username)),
              'error')
    else:
        user.delete()
        current_app.logger.warning(
            '%s deleted %s',
            cu.username,
            username)
        flash(_('User %(name)s has been deleted.',
                name=b(username)),
              'success')
    return redirect(url_for('admin.auth_user_list'))


@bp.route('/auth/user/<id>/reset/failed/logins/')
@permission_required('AUTH_ADMIN-USER-RESET_FAILED_LOGINS')
def auth_user_reset_failed_logins(id):
    user = User.query.get_or_404(id)
    user.failed_attempts = 0
    user.update()
    flash(_('Failed login attepts for user %(name)s has been reset',
            name=b(user.name)),
          'success')
    return redirect(url_for('admin.auth_user_list'))


@bp.route('/auth/role/')
@register_menu(
    bp,
    '.admin.auth.role',
    _('Roles'),
    order=20,
    icon='boxes',
    visible_when=lambda: cu.hp('AUTH_ADMIN-ROLE-LIST'))
@permission_required('AUTH_ADMIN-ROLE-LIST')
def auth_role_list():
    role_list = Role.query.all()
    form = AdminRoleCreateForm()
    return render_template(
        'auth/admin.role.list.html.j2',
        role_list=role_list,
        form=form,
    )


@bp.route('/auth/role/create/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.admin.auth.role.create',
    _('Create Role'),
    order=10,
    type='primary',
    icon='plus-square',
    visible_when=lambda: False,
    pagemenu=lambda: cu.hp('AUTH_ADMIN-ROLE-CREATE'))
@permission_required('AUTH_ADMIN-ROLE-CREATE')
def auth_role_create():
    permissions = Perm.query.all()
    form = AdminRoleCreateForm()
    if form.validate_on_submit():
        role = Role()
        form.populate_obj(role)
        if role.update():
            flash(_('Role %(name)s has been created.',
                    name=b(role.name)), 'success')
        for permission in permissions:
            if permission.name in request.form.getlist('permissions'):
                role.add_permission(permission)
            else:
                role.remove_permission(permission)
        return redirect(url_for('admin.auth_role_list'))
    return render_template(
        'auth/admin.role.edit.html.j2',
        form=form,
        permissions=permissions,
    )


@bp.route('/auth/role/<name>/')
@permission_required('AUTH_ADMIN-ROLE-READ')
@register_menu(
    bp,
    '.admin.auth.role.read',
    _('View'),
    order=20,
    type='primary',
    icon='eye',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(name='role'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-ROLE-READ'))
def auth_role_read(name):
    role = Role.query.filter_by(name=name).first_or_404()
    return render_template('auth/admin.role.read.html.j2', role=role)


@bp.route('/auth/role/<name>/edit/', methods=['GET', 'POST'])
@permission_required('AUTH_ADMIN-ROLE-EDIT')
@register_menu(
    bp,
    '.admin.auth.role.edit',
    _('Edit'),
    order=30,
    type='light',
    icon='pen',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(name='role'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-ROLE-EDIT'))
def auth_role_edit(name):
    role = Role.query.filter_by(name=name).first_or_404()
    permissions = Perm.query.all()
    form = AdminRoleForm(obj=role)
    if form.validate_on_submit():
        form.populate_obj(role)
        if role.update():
            flash(_('Role %(name)s was updated sucessfuly.',
                    name=b(role.name)), 'success')
        else:
            flash(_('Role %(name)s could not be updated.', name=b(role.name)),
                  'danger')
        for permission in permissions:
            if permission.name in request.form.getlist('permissions'):
                role.add_permission(permission)
            else:
                role.remove_permission(permission)
        return redirect(url_for('admin.auth_role_list'))
    return render_template('auth/admin.role.edit.html.j2',
                           form=form,
                           role=role,
                           permissions=permissions)


@bp.route('/auth/role/<name>/delete/')
@permission_required('AUTH_ADMIN-ROLE-DELETE')
@register_menu(
    bp,
    '.admin.auth.role.delete',
    _('Delete'),
    order=40,
    type='danger',
    icon='trash',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(name='role'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-ROLE-DELETE'))
def auth_role_delete(name):
    role = Role.query.filter_by(name=name).first_or_404()
    if role.users.all():
        flash(
            _('Role {name} has users assigned. You cannot delete it.'.format(
                name=b(name))),
            'danger')
        return redirect(url_for('admin.auth_role_list'))
    role.delete()
    flash(_('Role {name} has been deleted.'.format(name=b(name))),
          'success')
    return redirect(url_for('admin.auth_role_list'))


@bp.route('/auth/role/<name>/users/', methods=['GET', 'POST'])
@permission_required('AUTH_ADMIN-ROLE-USERS')
@register_menu(
    bp,
    '.admin.auth.role.users',
    _('Users'),
    order=50,
    type='light',
    icon='user',
    visible_when=lambda: False,
    endpoint_arguments_constructor=lambda: dict(name='role'),
    itemmenu=lambda: cu.hp('AUTH_ADMIN-ROLE-USERS'))
def auth_role_users(name):
    role = Role.query.filter_by(name=name).first_or_404()
    users = User.query
    form = AdminUserRoleForm()

    # Filter out all app admins
    for admin in current_app.config['RUNE_ADMINS']:
        users = users.filter(User.email != admin)

    if form.validate_on_submit():
        selected_users = request.form.getlist('users')
        role.update_users(users, selected_users)
        flash(_('Roles updated for the selected users.'), 'success')
        return redirect(url_for('admin.auth_role_list'))

    return render_template('auth/admin.role.users.html.j2',
                           form=form,
                           users=users,
                           role=role)


@bp.route('/auth/permission/')
@register_menu(
    bp,
    '.admin.auth.permission',
    _('Permissions'),
    order=30,
    visible_when=lambda: cu.hp(
        'AUTH_ADMIN-PERMISSION-LIST'),
    icon='box')
@permission_required('AUTH_ADMIN-PERMISSION-LIST')
def auth_permission_list():
    permissions = Perm.query.all()
    return render_template('auth/admin.permission.list.html.j2',
                           permissions=permissions)
