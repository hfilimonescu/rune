from datetime import date, timedelta

from flask_babel import lazy_gettext as _
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm

from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError


from rune.config import Config

from rune.util.text import b


class MessageForm(FlaskForm):
    # According to the links below this can be used successfuly to
    # set the default language of the message to the current users
    # locale. However this messes things up when editing an already
    # existing message since it changes the form locale to the current
    # user locale instead of keeping the message locale.
    # The correct solution is to initialize the form with
    # `current_user.locale` only in `admin.main_sysmsg_create` endpoint.
    #
    # https://stackoverflow.com/a/21338304
    # https://github.com/miguelgrinberg/microblog/issues/80#issuecomment-362934091
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.locale.data = current_user.locale

    locale = SelectField(
        _('Language'),
        choices=Config.RUNE_LANGUAGES,
        validators=[DataRequired()],
    )
    body = PageDownField(
        _('Message'),
        render_kw={
            'autofocus': 'autofocus',
            'rows': 10,
            'only_input': 'True',
        },
    )
    start_date = DateField(
        _('Start Date'),
        default=date.today(),
        validators=[DataRequired()]
    )
    end_date = DateField(
        _('End Date'),
        default=date.today() + timedelta(days=7),
        validators=[DataRequired()]
    )
    submit = SubmitField(_('Save'))

    def validate_end_date(self, end):
        if end.data < self.start_date.data:
            raise ValidationError(
                _('End date %(end)s is smaller than the start date %(start)s.',
                  end=b(self.end_date.data), start=b(self.start_date.data)))
