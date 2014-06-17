from random import choice
from hashlib import sha512
from string import ascii_uppercase, ascii_lowercase, digits
import smtplib
from configobj import ConfigObj

config = ConfigObj('app.config')

class Authentication:

    @staticmethod
    def user_exists(email):
        user = User.query.filter(User.email==email.lower()).first()
        return user != None


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

        if user.password == Authentication.salt_and_hash(password, user.salt) and user.activated == True:
            return True
        else:
            return False


class Email:

    @staticmethod
    def send(to_email, subject, body):

        content = 'To:{0}\nFrom:{1}\nSubject:{2}\n{3}\n\n'.format(to_email, config['smtp_sender'], subject, body)
        smtp = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        smtp.starttls()
        smtp.login(config['smtp_username'], config['smtp_password'])
        smtp.sendmail(config['smtp_sender'], to_email, content)
