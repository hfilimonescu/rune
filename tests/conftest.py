import pytest

from rune import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "TeStKeY",
        }
    )
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        data = {
            "username": username,
            "password": password,
        }
        return self._client.post("/auth/login/", data=data)

    def logout(self):
        return self._client.get("/auth/logout/")


@pytest.fixture
def auth(client):
    return AuthActions(client)


# Use the docstring to name the tests
# def pytest_itemcollected(item):
#     par = item.parent.obj
#     node = item.obj
#     pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
#     suf = node.__doc__.strip() if node.__doc__ else node.__name__
#     if pref or suf:
#         item._nodeid = ': '.join((pref, suf))
