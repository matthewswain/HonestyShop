from random import choice
from hashlib import sha512
from string import ascii_uppercase, ascii_lowercase, digits
import smtplib

class Authentication:

    @staticmethod
    def user_exists(email):
        user = User.query.filter(User.email==email).first()
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

        if user.password == Authentication.salt_and_hash(password, user.salt):
            return True
        else:
            return False


class Email:

    @staticmethod
    def send(to_email, from_email, subject, body):

        content = 'To:{0}\nFrom:{1}\nSubject:{2}\n{3}\n\n'.format(to_email, from_email, subject, body)
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login('username', 'password')
        smtp.sendmail(from_email, to_email, content)