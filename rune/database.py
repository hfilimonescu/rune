from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_continuum.plugins.flask import fetch_current_user_id

from . import db


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any((isinstance(id, (str, bytes)) and id.isdigit(),
                isinstance(id, (int, float))),):
            return cls.query.get(int(id))
        return None

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


class AuditMixin(object):
    __table_args__ = {'extend_existing': True}

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    change_time = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    @declared_attr
    def create_id(cls):
        return db.Column(db.Integer, db.ForeignKey('auth_users.id'),
                         default=fetch_current_user_id)

    @declared_attr
    def create_by(cls):
        return db.relationship(
            'User',
            primaryjoin='%s.create_id == User.id' % cls.__name__,
            enable_typechecks=False)

    @declared_attr
    def change_id(cls):
        return db.Column(db.Integer, db.ForeignKey('auth_users.id'),
                         onupdate=fetch_current_user_id)

    @declared_attr
    def change_by(cls):
        return db.relationship(
            'User',
            primaryjoin='%s.change_id == User.id' % cls.__name__,
            enable_typechecks=False)


class SoftDeleteMixin:
    __table_args__ = {"extend_existing": True}

    delete_flag = db.Column(db.Boolean, server_default=None,
                            default=None, nullable=True)

    @classmethod
    def sget(cls, id=None):
        if id:
            if any((isinstance(id, (str, bytes)) and id.isdigit(),
                    isinstance(id, (int, float))),):
                return cls.query.filter_by(id=int(id)).all()
        return cls.query.filter_by(delete_flag=False).all()

    def delete(self, commit=True):
        return self.sdelete(commit)

    def sdelete(self, commit=True):
        setattr(self, 'delete_flag', True)
        return commit and self.save() or self
