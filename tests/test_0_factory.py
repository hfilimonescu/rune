import pytest
from rune import create_app


class TestFactory:
    """Factory"""
    app = create_app(
        {
            "TESTING": True,
            "RHHR_API_ENABLED": True,
            "SQLALCHEMY_TRACK_MODIFICATIONS": True,
        }
    )

    def test_config(self):
        """Test create_app w/o `testing` config"""
        assert not create_app().testing

    def test_testing_config(self):
        """Test create_app w/ `testing` config"""
        assert create_app({"TESTING": True}).testing

    def test_testing_app(self, app):
        """Testing app ist configured for testing"""
        assert app.testing
