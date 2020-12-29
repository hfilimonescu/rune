from datetime import date
from time import sleep

from apifairy import arguments, body, other_responses, response
from flask import abort, json, redirect, request
from flask_login import current_user
from rune.util.url import url_for
from rune_api.bp import bp
from rune_auth.decorators import permission_required as pr

from rune_main.models import Notification
from rune_main.schemes import (FilterSchema, notification_schema,
                               notifications_schema)


@bp.route('/v1/main/notifications/', methods=['POST'])
@body(notification_schema)
@response(notification_schema)
@pr('MAIN_ADMIN-SYSMSG-CREATE')
def main_notification_create(notification):
    """Create Notification"""
    notification.author_id = current_user.id
    notification.update()

    return notification, 201


@bp.route('/v1/main/notifications/', methods=['GET'])
@response(notifications_schema)
@body(FilterSchema)
@pr('MAIN_ADMIN-SYSMSG-LIST')
def main_notification_list(body_filter):
    """Notification List
    returns a list of notifications.
    """
    if len(body_filter) == 0:
        return Notification.read()

    resources = Notification.query

    all = body_filter.get('all')

    if not all:
        id = body_filter.get('id')
        author_id = body_filter.get('author_id')
        locale = body_filter.get('locale')
        start_date = body_filter.get('start_date')
        end_date = body_filter.get('end_date')

        if id:
            resources = resources.filter_by(id=id)
        if author_id:
            resources = resources.filter_by(author_id=author_id)
        if locale:
            resources = resources.filter_by(locale=locale)
        if start_date:
            resources = resources.filter(Notification.start_date <= start_date)
        if end_date:
            resources = resources.filter(Notification.end_date >= end_date)

    resources = resources.all()

    return resources


@bp.route('/v1/main/notifications/', methods=['PUT'])
@response(notification_schema)
@body(notification_schema)
@pr('MAIN_ADMIN-SYSMSG-EDIT')
def main_notification_update(notification):
    """Edit Notifications"""
    if not Notification.query.get(notification.id):
        abort(404)

    notification.author_id = current_user.id
    notification.update()

    return notification


@bp.route('/v1/main/notifications/', methods=['DELETE'])
@pr('MAIN_ADMIN-SYSMSG-DELETE')
@response(notification_schema)
def main_notification_delete():
    """Delete Notification"""
    data = request.get_json()

    notification = Notification.query.get(data.get('id'))

    if not notification:
        abort(404)

    notification.delete()

    return '', 204
