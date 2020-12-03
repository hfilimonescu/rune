""" For a complete list of options regarding middleware options
have a look at the link below:
https://stackoverflow.com/questions/51691730/flask-middleware-for-specific-route/51820573
"""


class Test:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print('go!')
        return self.app(environ, start_response)
