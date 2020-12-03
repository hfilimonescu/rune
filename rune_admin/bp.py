from flask import Blueprint
from flask_login import login_required


bp = Blueprint(
    'admin', __name__,
    url_prefix='/admin',
    template_folder='templates',
    static_folder='static',
)


@bp.before_request
@login_required
def before_request():
    """We are protecting all admin endpoints with `login_required`."""
    pass
