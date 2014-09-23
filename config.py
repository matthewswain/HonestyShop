class BaseConfig(object):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///honesty.db'
    SECRET_KEY = ''
    BASE_URL = ''

    SMTP_PORT = 25
    SMTP_USERNAME = ''
    SMTP_PASSWORD = ''
    SMTP_SENDER = ''
