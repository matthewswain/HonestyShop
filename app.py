from flask import Flask, render_template, url_for, request, redirect, session
from functools import wraps
app = Flask(__name__)


## Debug section
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
    

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('home'))
    else:
        return render_template('login.html', urls=get_urls())


@app.route('/logout/')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register/')
def register():
    return render_template('register.html', urls=get_urls())


if __name__ == '__main__':
    app.secret_key = 'Development secret key'
    app.run(debug=True)
