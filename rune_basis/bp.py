from flask import Blueprint


bp = Blueprint(
    'basis',
    __name__,
    url_prefix='/basis',
    template_folder='templates',
    static_folder='static',
)
