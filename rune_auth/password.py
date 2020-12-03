import secrets


def password_generator(length=None):
    return secrets.token_urlsafe(length)
