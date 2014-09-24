from random import choice
from hashlib import sha512
from string import ascii_uppercase, ascii_lowercase, digits
import smtplib
from email.mime.text import MIMEText


class Authentication(object):

    @staticmethod
    def user_exists(email):
        user = User.query.filter(User.email == email.lower()).first()
        return user is not None

    @staticmethod
    def random_string(length):
        string = ''
        for i in range(0, length):
            string += choice(ascii_uppercase + ascii_lowercase + digits)

        return string

    @staticmethod
    def salt_and_hash(password, salt):
        return sha512(password + salt).hexdigest()

    @staticmethod
    def authenticate(user, password):

        if user.password == Authentication.salt_and_hash(password, user.salt) and user.activated:
            return True
        else:
            return False


class Email(object):

    @staticmethod
    def send(to_email, subject, body):

        message = MIMEText(body, 'html')
        message['To'] = to_email
        message['From'] = app.config['SMTP_SENDER']
        message['Subject'] = subject

        smtp = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        smtp.starttls()
        smtp.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        smtp.sendmail(app.config['SMTP_SENDER'], to_email, message.as_string())
        smtp.quit()