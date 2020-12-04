from bleach import clean, linkify
from datetime import date
from markdown import markdown
from sqlalchemy import and_
from dateutil.parser import parse


from flask import g


from rune import db
from rune.database import CRUDMixin


from . import conf_markdown as mkd


class Notification(CRUDMixin, db.Model):
    __tablename__ = 'main_messages'
    locale = db.Column(db.String(5), default='en')
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    author = db.relationship('User',
                             foreign_keys=[author_id],
                             backref=db.backref('messages', lazy='dynamic'))
    start_date = db.Column(db.Date,
                           nullable=False,
                           default=date.today())
    end_date = db.Column(db.Date,
                         nullable=False,
                         default=date.today())

    @property
    def visible(self):
        return self.start_date <= date.today() <= self.end_date

    @property
    def expired(self):
        return self.end_date < date.today()

    @staticmethod
    def read():
        messages = Notification.query.filter(
            and_(
                Notification.start_date <= date.today(),
                Notification.end_date >= date.today(),
                Notification.locale == g.locale)).all()
        return messages

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = linkify(clean(markdown(value, output_format='html',
                                                  extensions=mkd.allowed_extensions),
                                         tags=mkd.allowed_tags,
                                         attributes=mkd.allowed_attrs,
                                         strip=True))

    def to_json(self):
        return {
            'id': self.id,
            'body': self.body_html,
            'author_id': self.author_id,
            'locale': self.locale,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    def from_json(self, data):
        allowed_fields = [
            'locale',
            'body',
            'author_id',
        ]

        date_fields = [
            'start_date',
            'end_date',
        ]

        for field in allowed_fields:
            print(data[field])
            try:
                setattr(self, field, data[field])
            except KeyError:
                pass

        for field in date_fields:
            try:
                setattr(self, field, parse(data[field]))
            except KeyError:
                pass


db.event.listen(Notification.body, 'set', Notification.on_changed_body)
