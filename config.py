class BaseConfig(object):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///honesty.db'
    SECRET_KEY = 'a'
    BASE_URL = 'http://localhost'

    SMTP_PORT = 25
    SMTP_USERNAME = '2c8c775d-b3d7-4df0-9fd9-d285d5dba925'
    SMTP_PASSWORD = '2c8c775d-b3d7-4df0-9fd9-d285d5dba925'
    SMTP_SENDER = 'admin@honestybar.uk'
    SMTP_SERVER = 'smtp.postmarkapp.com'

    DEBUG = True
