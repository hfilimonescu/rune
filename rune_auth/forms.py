from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from rune.config import Config
from rune.util.text import b
from wtforms import (BooleanField, PasswordField, SelectField, StringField,
                     SubmitField)
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, Regexp, ValidationError)

from .models import Role, User


class LoginForm(FlaskForm):
    username = StringField(
        _('Username'),
        render_kw={'autofocus': 'autofocus'},
        validators=[DataRequired(), Length(1, 64)]
    )
    password = PasswordField(
        _('Password'),
        validators=[DataRequired()]
    )
    remember_me = BooleanField(
        _('Remember me'),
        default=False
    )
    submit = SubmitField(_('Login'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        _('Old password'),
        render_kw={'autofocus': 'autofocus'},
        validators=[DataRequired()]
    )
    password = PasswordField(
        _('New password'),
        validators=[
            DataRequired(),
            Length(5, 32),
            # Regexp('[A-Za-z0-9@#$%^&+=]'),
            EqualTo('password2', message=_('Passwords must match'))
        ]
    )
    password2 = PasswordField(
        _('Confirm new password'),
        validators=[
            DataRequired(),
            Length(5, 32)
        ]
    )
    submit = SubmitField(_('Update Password'))


class ResetPasswordForm(FlaskForm):
    email = StringField(
        _('Email'),
        render_kw={'autofocus': 'autofocus'},
        validators=[
            Email(),
            DataRequired(),
            Length(1, 64),
        ]
    )
    submit = SubmitField(_('Reset Password'))


class PreferenceForm(FlaskForm):
    name = StringField(
        _('Key'),
        render_kw={'autofocus': 'autofocus'},
        validators=[
            DataRequired(),
            Length(1, 64),
        ]
    )
    value = StringField(
        _('Value'),
        validators=[
            Optional(),
            Length(0, 64),
        ]
    )
    submit = SubmitField(_('Save'))


class AdminUserForm(FlaskForm):
    username = StringField(
        _('Username'),
        render_kw={'readonly': 'readonly'}
    )
    name = StringField(
        _('Full Name'),
        render_kw={'autofocus': 'autofocus'},
        validators=[
            DataRequired(),
            Length(1, 64),
        ]
    )
    email = EmailField(
        _('Email'),
        validators=[
            DataRequired(),
            Length(6, 64),
            Email(),
        ]
    )
    birthdate = DateField(
        _('Birthdate'),
        validators=[Optional()]
    )
    location = StringField(
        _('Location'),
        validators=[
            Optional(),
            Length(1, 64),
        ]
    )
    locale = SelectField(
        _('Language'),
        choices=Config.RUNE_LANGUAGES,
        default=Config.RUNE_DEFAULT_LOCALE
    )
    active = BooleanField(_('Active User'), default=True)


class AdminUserCreateForm(AdminUserForm):
    username = None
    submit = SubmitField(_('Save'))

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first() is not None:
            raise ValidationError(
                _('Email %(mail)s is already registered.', mail=b(email.data)))


class AdminUserEditForm(AdminUserForm):
    submit = SubmitField(_('Save'))


class AdminUserRoleForm(FlaskForm):
    submit = SubmitField(_('Assign Roles'))


class AdminRoleForm(FlaskForm):
    name = StringField(
        _('Name'),
        render_kw={'autofocus': 'autofocus'},
        validators=[
            DataRequired(),
            Length(5, 32),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_]*$', 0,
                _('Role names are allowed only letters, numbers, '
                  'or underscores'),
            ),
        ]
    )
    description = StringField(
        _('Description'),
        validators=[
            DataRequired(),
            Length(1, 128),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_ ]*$',
                0,
                _('Role descriptions are allowed only letters, numbers, '
                  'or underscores')
            ),
        ]
    )
    submit = SubmitField(_('Save'))


class AdminRoleCreateForm(AdminRoleForm):
    def validate_name(self, name):
        role = Role.query.filter_by(name=name.data).first()
        if role is not None:
            raise ValidationError(_('Please use a different name.'))
