from datetime import date

from rune import ma

from rune_main.models import Notification


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        include_fk = True
        load_instance = True

        fields = [
            'id',
            'body',
            'body_html',
            'author_id',
            'locale',
            'start_date',
            'end_date',
        ]


class FilterSchema(ma.Schema):
    author_id = ma.Int()
    locale = ma.Str()
    all = ma.Bool()
    id = ma.Int()
    start_date = ma.Date()
    end_date = ma.Date()


notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
