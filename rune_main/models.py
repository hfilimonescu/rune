from datetime import date, timedelta

from bleach import clean, linkify
from dateutil.parser import parse
from flask import g
from markdown import markdown
from rune import db
from rune.database import CRUDMixin
from sqlalchemy import and_

from . import conf_markdown as mkd


class Notification(CRUDMixin, db.Model):
    __tablename__ = 'main_messages'
    locale = db.Column(db.String(5), default='en')
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    author = db.relationship(
        'User',
        foreign_keys=[author_id],
        backref=db.backref('messages', lazy='dynamic'))
    start_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today())
    end_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today() + timedelta(days=7))

    @property
    def visible(self):
        return self.start_date <= date.today() <= self.end_date

    @property
    def expired(self):
        return self.end_date < date.today()

    @staticmethod
    def read():
        notifications = Notification.query.filter(
            and_(
                Notification.start_date <= date.today(),
                Notification.end_date >= date.today(),
                Notification.locale == g.locale)).all()
        return notifications

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = linkify(
            clean(
                markdown(
                    value,
                    output_format='html',
                    extensions=mkd.allowed_extensions,
                ),
                tags=mkd.allowed_tags,
                attributes=mkd.allowed_attrs,
                strip=True,
            )
        )


db.event.listen(Notification.body, 'set', Notification.on_changed_body)
