from datetime import datetime, timedelta
from time import time

from flask import abort, current_app
from flask_login import AnonymousUserMixin, UserMixin
from rune import db
from rune.database import CRUDMixin
from rune.util.url import url_for
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

from rune_auth import login

user_role = db.Table(
    'auth_user_roles',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey(
            'auth_users.id',
            ondelete='CASCADE',
        ),
    ),
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey(
            'auth_roles.id',
            ondelete='CASCADE',
        ),
    ),
)


role_permission = db.Table(
    'auth_role_permissions',
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey(
            'auth_roles.id',
            ondelete='CASCADE',
        ),
    ),
    db.Column(
        'permission_id',
        db.Integer,
        db.ForeignKey(
            'auth_permissions.id',
            ondelete='CASCADE',
        ),
    ),
)


class User(CRUDMixin, UserMixin, db.Model):
    __tablename__ = 'auth_users'
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    locale = db.Column(db.String(5), default='en')
    location = db.Column(db.String(64))
    username = db.Column(db.String(32), nullable=False, unique=True)
    birthdate = db.Column(db.Date)

    password_hash = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(256), index=True, unique=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    force_pwd_change = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, default=False)
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)

    type = db.Column(db.String(20))
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'user',
    }

    _roles = db.relationship(
        'Role',
        secondary=user_role,
        backref=db.backref('users', lazy='dynamic'),
    )
    roles = association_proxy('_roles', 'name')

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.type}: {self.name}'

    @validates('location')
    def validate_location(self, key, value):
        if not value:
            return None
        return value

    @property
    def password(self):
        raise AttributeError('´password´ is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        self.token = None  # if user is changing passwords, also revoke token

    def verify_password(self, password):
        result = check_password_hash(self.password_hash, password)
        if not result:
            self.failed_attempts += 1
        else:
            self.failed_attempts = 0
        self.update()
        return result

    @property
    def permissions(self):
        permissions = []
        names = []
        for role in self._roles:
            permissions += role.permissions
        for permission in permissions:
            names.append(permission.name)
        return names

    def has_permission(self, permission):
        if self.is_admin or permission.upper() in self.permissions:
            return True
        return False

    def hp(self, permission):
        return self.has_permission(permission)

    def has_role(self, role):
        if self.is_admin:
            return True
        if role in self.roles:
            return True
        return False

    def add_role(self, role):
        if role not in self._roles:
            self._roles.append(role)
            self.update()

    def update_roles(self, available_roles=[], selected_roles=[]):
        for role in available_roles:
            if role.name in selected_roles and role not in self._roles:
                self._roles.append(role)
            if role.name not in selected_roles and role in self._roles:
                self._roles.remove(role)
        self.update()

    def remove_role(self, role):
        if role in self._roles:
            self._roles.remove(role)
            self.update()

    @property
    def _is_ddic(self):
        if self.is_admin:
            return True
        return False

    @property
    def is_admin(self):
        if self.email in current_app.config['RUNE_ADMINS']:
            return True
        return False

    def to_dict(self):
        """Export user to a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'active': self.active,
            'is_admin': self.is_admin,
            'force_pwd_change': self.force_pwd_change,
            'type': self.type,
            'failed_attempts': self.failed_attempts,
            'roles': [role for role in self.roles],
            'permissions': self.permissions,
            'links': [
                {
                    'url': url_for('api.auth_user_details', username=self.username),
                    'text': 'Details'
                },
                {
                    'url': url_for('api.auth_user_delete', username=self.username),
                    'text': 'Delete'
                },
            ]

        }

    def from_dict(self, data, new_user=False):
        allowed_fields = [
            'username',
            'email',
            'name',
            'birthdate',
            'locale',
            'location',
        ]

        for field in allowed_fields:
            if field in data:
                setattr(self, field, data[field])

        if new_user and 'password' in data:
            self.set_password(data['password'])

    @staticmethod
    def on_changed_email(target, value, oldvalue, initiator):
        """Update the `username` when the email changes."""
        target.username = value.split('@')[0]

    @staticmethod
    def on_changed_failed_attempts(target, value, oldvalue, initiator):
        """Deactivate user if the failed attempts limit is reached."""
        if target.failed_attempts >= 5:
            target.active = False


db.event.listen(User.email, 'set', User.on_changed_email)
db.event.listen(User.failed_attempts, 'set', User.on_changed_failed_attempts)


class AnonymousUser(AnonymousUserMixin):
    pass


login.anonymous_user = AnonymousUser


class Role(CRUDMixin, db.Model):
    """
    TODO:
     - add logic to automatically set `MENU-*` if one `MENU-*-*` is set
     - add logic to automatically remove `MENU-*` if all `MENU-*-*` are removed
    """
    __tablename__ = 'auth_roles'
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(128))
    group = db.Column(db.String(120))
    permissions = db.relationship(
        'Perm', secondary=role_permission, backref='roles')

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'[Role: {self.name}]'

    def add_permission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.update()

    def remove_permission(self, permission):
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.update()

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        target.group = value.split('_')[0]

    def update_users(self, available=[], selected=[]):
        for user in available:
            if user.username in selected and user not in self.users:
                self.users.append(user)
            if user.username not in selected and user in self.users:
                self.users.remove(user)
        self.update()


db.event.listen(Role.name, 'set', Role.on_changed_name)


class Perm(CRUDMixin, db.Model):
    __tablename__ = 'auth_permissions'
    name = db.Column(db.String(120), unique=True)
    group = db.Column(db.String(120))

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'[Permission: {self.name}]'

    @validates('name')
    def validate_name(self, key, value):
        return value.upper()

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        target.group = value.split('-')[0]


db.event.listen(Perm.name, 'set', Perm.on_changed_name)


class AuthUserPreference(CRUDMixin, db.Model):
    __tablename__ = 'auth_user_preferences'
    name = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    user = db.relationship('User',
                           foreign_keys=[user_id],
                           backref=db.backref('preferences', lazy='dynamic'))

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'[Preference: {self.name}]'

    @validates('name')
    def validate_name(self, key, value):
        return value.upper()

    @validates('value')
    def validate_value(self, key, valoare):
        if not valoare:
            return None
        return valoare


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
