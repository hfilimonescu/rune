from datetime import date
from time import sleep


from flask import abort, json, redirect, request


from rhhr.util.url import url_for

from rune_api.bp import bp
from rune_main.models import Notification


@bp.route('/v1/notifications/', methods=['POST'])
def notification_notification_create():
    json_data = request.get_json()

    notification = Notification()
    notification.from_json(json_data)
    notification.update()

    return notification.to_json(), 201


@bp.route('/v1/notifications/', methods=['GET'])
def notification_notification_list():
    resources = Notification.query

    all = request.args.get('all')

    if not all:
        id = request.args.get('id')
        author_id = request.args.get('author_id')
        locale = request.args.get('locale')
        start_date = request.args.get('start_date', date.today())
        end_date = request.args.get('end_date', date.today())

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

    if not resources:
        abort(404, 'The requested resource was not found on the server.')

    return {'notifications': [item.to_json() for item in resources]}


@ bp.route('/v1/notifications/', methods=['PUT'])
def notification_notification_update():
    json_data = request.get_json()

    notification = Notification.query.get(json_data['id'])

    if not notification:
        abort(404, 'The requested resource was not found on the server.')

    notification.from_json(json_data)
    notification.update()

    return notification.to_json()


@ bp.route('/v1/notifications/', methods=['DELETE'])
def main_notification_delete():
    json_data = request.get_json()

    notification = Notification.query.get(json_data['id'])

    if not notification:
        abort(404, 'The requested resource was not found on the server.')

    notification.delete()

    return '', 204
