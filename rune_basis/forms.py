from wtforms import SubmitField

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm


class AdminSubmitForm(FlaskForm):
    submit = SubmitField(_('Install'))
