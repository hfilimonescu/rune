from flask import _request_ctx_stack, current_app, request
from flask import url_for as _url_for


def url_for(*args, **kwargs):
    """´url_for´ replacement that works even when there is no request context.
    """
    if '_external' not in kwargs:
        kwargs['_external'] = False
        if request.is_json:
            kwargs['_external'] = True
    reqctx = _request_ctx_stack.top
    if reqctx is None:
        if kwargs['_external']:
            raise RuntimeError(
                'Cannot generate external URLs without a request context.')
        with current_app.test_request_context():
            return _url_for(*args, **kwargs)
    return _url_for(*args, **kwargs)
