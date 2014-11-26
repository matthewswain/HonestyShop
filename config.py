class BaseConfig(object):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///honesty.db'
    SECRET_KEY = 'a'
    BASE_URL = 'http://localhost'

    SMTP_PORT = 25
    SMTP_USERNAME = '90e9fb2a-c63a-4f5c-961a-695ea4c81f36'
    SMTP_PASSWORD = '90e9fb2a-c63a-4f5c-961a-695ea4c81f36'
    SMTP_SENDER = 'admin@honestybar.uk'
    SMTP_SERVER = 'smtp.postmarkapp.com'

    DEBUG = False
