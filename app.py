from flask import Flask, render_template, url_for, request, redirect, session
from functools import wraps
from database import session as db
from models import User
from security import Authentication
app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function              


@app.route('/')
@login_required
def home():
    return 'Hello {0}'.format(session['email'])


def get_urls():
    return {
        'home':url_for('home'),
        'about':'',
        'workflows':'',
        'register':url_for('register'),
        'login':url_for('login')
    }


@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.get(request.form['email'])
        if user != None and  Authentication.authenticate(user, request.form['password']):
             session['email'] = request.form['email']
             return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html', urls=get_urls())


@app.route('/logout/')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register/', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if User.get(request.form['email']) == None:
            user = User(request.form['email'], request.form['password'])
#            return user.url_part
        return 'Already exists.'
    else:
        return render_template('register.html', urls=get_urls())


@app.route('/buy/', methods=['GET','POST'])
def buy():
    if request.method == 'POST':
        return request.form['item_id']
    else:
        return render_template('buy.html', urls=get_urls())


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


if __name__ == '__main__':
    app.secret_key = 'Development secret key'
    app.run(debug=True)
