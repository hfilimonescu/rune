class Config:
    BABEL_DOMAIN = 'rhhr'
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(
        os.path.dirname(__file__), 'translations')

    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RUNE_ADMINS = [
        'rune@rhhr.ro',
        'ddic@rhhr.ro',
        'admin@rhhr.ro'
    ]
    RUNE_DEFAULT_LOCALE = 'de'
    RUNE_LANGUAGES = [
        ('de', 'Deutsch'),
        ('en', 'English'),
        ('ro', 'Română'),
    ]
    RUNE_LOG_STDOUT = False
    RUNE_NAME = 'Rune'
    RUNE_UI_APP_LOGO = 'hagalaz.png'

    MAIL_SERVER = None
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEBUG = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    # MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = False
    # MAIL_ASCII_ATTACHMENTS = False
    MAIL_DEFAULT_SENDER = (RUNE_NAME, RUNE_ADMINS[0])
