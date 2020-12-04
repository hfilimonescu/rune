from sqlalchemy import and_

from flask import abort, current_app, flash, redirect
from flask import render_template, request, session

from flask_babel import lazy_gettext as _
from flask_babel import ngettext
from flask_login import current_user, login_required, login_user, logout_user
from flask_menu import register_menu


from rune.util.text import b
from rune.util.url import url_for

from .bp import bp
from .emails import user_reset_password
from .forms import LoginForm, ChangePasswordForm, ResetPasswordForm
from .forms import PreferenceForm
from .models import User, AuthUserPreference
from .password import password_generator


@bp.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        if current_user.force_pwd_change \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint[:7] != 'static.'\
                and request.endpoint[:13] != 'debugtoolbar.':
            return redirect(url_for('auth.change_password'))


@bp.route('/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.auth',
    _('Login'),
    order=0,
    visible_when=lambda: False,
)
def login():
    if current_user.is_authenticated:
        flash(_('You were already authenticated as %(name)s.',
                name=b(current_user.name)), 'info')
        if session['preferences']:
            session.pop('preferences', None)
        if session['locale']:
            session.pop('locale', None)

        logout_user()

    form = LoginForm()

    if not current_app.config['RUNE_AUTH_LOGIN_REMEMBER']:
        form.remember_me = None

    if form.validate_on_submit():
        _fails = 0

        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash(_('Invalid username or password.'), 'error')
            return redirect(url_for('auth.login'))

        _fails = user.failed_attempts

        if not user.verify_password(form.password.data):
            flash(_('Invalid username or password.'), 'error')
            return redirect(url_for('auth.login'))

        if _fails > 0:
            flash(ngettext('You have %(num)d failed login attempt.',
                           'You have %(num)d failed login attempts.',
                           num=_fails),
                  'warning')

        login_user(user)

        session['locale'] = user.locale
        session['preferences'] = {}

        for preference in user.preferences:
            session['preferences'][preference.name] = preference.value

        return redirect(request.args.get('next') or url_for('main.index'))

    return render_template('auth/routes.login.html.j2', form=form)


@bp.route('/logout/')
@register_menu(
    bp,
    '.auth.logout',
    _('Logout'),
    order=90,
    visible_when=lambda: current_user.is_authenticated,
    icon='sign-out-alt',
    divided=True)
@login_required
def logout():
    logout_user()

    session.pop('preferences', None)
    session.pop('locale', None)

    flash(_('You have been logged out.'), 'info')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(_('Please provide a valid email.'), 'error')
            return redirect(url_for('auth.reset_password'))
        if not user.active:
            flash(_('Your account is not active. Please contact the administrator.'),
                  'error')
            return redirect(url_for('auth.login'))
        if user.force_pwd_change:
            flash(_('You have already resetted your password!'), 'info')
            return redirect(url_for('auth.login'))

        password = password_generator(16)

        if current_app.config['DEBUG']:
            print(password)

        user.force_pwd_change = True
        user.password = password

        form.populate_obj(user)
        if user.update():
            flash(_('Your password has been reset. Check your Email account.'),
                  'success')
            user_reset_password(user, password)

        return redirect(url_for('auth.login'))
    return render_template('auth/routes.reset_password.html.j2', form=form)


@bp.route('/change_password/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.auth.change_password',
    _('Change Password'),
    order=30,
    visible_when=lambda: current_user.is_authenticated,
    icon='unlock-alt')
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.force_pwd_change = False
            if current_user.update():
                flash(_('Your password has been updated.'), 'success')
                return redirect(url_for('auth.login'))
        else:
            flash(_('Invalid password.'), 'danger')
    return render_template("auth/routes.change_password.html.j2", form=form)


@bp.route('/profile/')
@register_menu(
    bp,
    '.auth.profile',
    _('My Profile'),
    order=10,
    visible_when=lambda: current_user.is_authenticated,
    icon='user')
def profile():
    return render_template(
        'auth/admin.user.read.html.j2',
        user=current_user)


@bp.route('/preference/')
@register_menu(bp,
               'auth.preference',
               _('Preferences'),
               order=20,
               visible_when=lambda: current_user.is_authenticated,
               icon='sliders-h')
@login_required
def preferences():
    form = PreferenceForm()
    preferences = AuthUserPreference.query.filter_by(
        user_id=current_user.id).all()

    return render_template('auth/routes.preferences.html.j2',
                           form=form,
                           preferences=preferences,
                           user=current_user)


@bp.route('/preference/create/', methods=['GET', 'POST'])
@register_menu(
    bp,
    '.auth.preference.create',
    _('Add Preference'),
    icon='plus-square',
    order=10,
    type='primary',
    visible_when=lambda: False,
    pagemenu=lambda: True)
def preference_create():
    form = PreferenceForm()

    if form.validate_on_submit():
        exists = AuthUserPreference.query.filter(and_(
            AuthUserPreference.name == form.name.data,
            AuthUserPreference.user_id == current_user.id)).first()
        if exists:
            preference = AuthUserPreference.query.get(exists.id)
        else:
            preference = AuthUserPreference()
        form.populate_obj(preference)
        preference.user_id = current_user.id

        preference.update()

        session.pop('preferences', None)
        session['preferences'] = {}

        for pref in current_user.preferences:
            session['preferences'][pref.name] = pref.value

        flash(_('Preference %(name)s is set to %(value)s',
                name=b(preference.name), value=b(preference.value or 'False')),
              'success')

        return redirect(url_for('auth.preferences'))

    for field, errors in form.errors.items():
        for error in errors:
            flash(_('%(field)s: %(msg)s',
                    field=b(getattr(form, field).label.text),
                    msg=error),
                  'danger')

    return render_template('auth/routes.preferences.html.j2',
                           form=form,
                           user=current_user)


@bp.route('/preference/reload/')
@register_menu(
    bp,
    '.auth.preference.reload',
    _('Reload Preferences'),
    order=20,
    icon='redo-alt',
    type='info',
    visible_when=lambda: False,
    pagemenu=lambda: True)
def preference_reload():
    session.pop('preferences', None)
    session['preferences'] = {}

    for pref in current_user.preferences:
        session['preferences'][pref.name] = pref.value

    flash(_('Preferences for %(name)s have been reloaded.',
            name=b(current_user.name or current_user.username)), 'success')

    return redirect(url_for('auth.preferences'))
