from flask import Flask, render_template, url_for, request, redirect, session, make_response, flash, get_flashed_messages
from functools import wraps
from models import User, Item, Purchase, ActivationToken, PasswordToken, Payment, db
from forms import ItemForm, LoginForm, PaymentForm
from security import Authentication, Email
from configobj import ConfigObj

import traceback

config = ConfigObj('app.config')
app = Flask(__name__)
app.config.from_object('config.BaseConfig')

db.app = app
db.init_app(app)
dbs = db.session


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function              


def group_required(groups):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            user = User.get(session['email'])
            authorized = False

            for membership in user.memberships:
                if membership.group.name in groups:
                    authorized = True

            if not authorized:
                return redirect(url_for('home'))
            else:
                return f(*args, **kwargs)

        return decorated_function
    return decorator


def get_urls():
    return [
        ('Home', url_for('home')),
        ('Buy', url_for('buy')),
        ('History', url_for('history')),
        ('Logout', url_for('logout')),
    ]


@app.route('/')
@login_required
def home():
    data = {
        'nav_urls': get_urls(),
        'active_url': url_for('home')
    }
    return render_template('index.html', data=data)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.get(request.form['email'])
        if user is not None and Authentication.authenticate(user, request.form['password']):
            session['email'] = request.form['email']
            session['is_admin'] = user.is_member('admin')
            session.permanent = True
            return redirect(url_for('home'))
        else:
            flash('Login failed, please retry.', 'alert alert-danger')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', urls=get_urls(), form=form)


@app.route('/logout/')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.get(request.form['email']) is None:
            
            user = User(request.form['email'], request.form['password'])
            dbs.add(user)
            dbs.commit()

            token = ActivationToken(user)
            dbs.add(token)
            dbs.commit()

            activation_url = url_for('activate', url_part=token.url_part)
            activation_url = app.config['BASE_URL'] + activation_url
            email_body = render_template('email/register.html', activation_url=activation_url)

            try:
                Email.send(user.email, 'Honesty Shop - Activate Account', email_body)
                flash('Account created, please activate your account using the link in your welcome email.', 'alert alert-success')
            except:
                flash('There was a problem sending your activation email, please try again later.', 'alert alert-danger')

                dbs.delete(token)
                dbs.commit()

                dbs.delete(user)
                dbs.commit()


        else:
            flash('An account with that email address already exists, please login.', 'alert alert-warning')    

        return redirect(url_for('login'))

    else:
        return render_template('register.html', urls=get_urls(), form=form)


@app.route('/reset/', methods=['GET', 'POST'])
@app.route('/reset/<url_part>', methods=['GET'])
def reset(url_part=None):
    form = LoginForm(request.form)
    if request.method == 'POST':
        user = User.get(form.email.data)

        if user is not None:
            token = PasswordToken(user, form.password.data)
            dbs.add(token)
            dbs.commit()

            reset_url = url_for('reset') + token.url_part
            reset_url = app.config['BASE_URL'] + reset_url
            email_body = render_template('email/reset_password.html', reset_url=reset_url)

            try:
                Email.send(user.email, 'Honesty Shop - Reset Password', email_body)
                flash('Confirmation email sent, please click link within before using your new password.', 'alert alert-warning')
            except:
                flash('There was a problem sending your confirmation email, please try again later.', 'alert alert-danger')


        return redirect(url_for('login'))
    elif url_part is None:
        return render_template('reset_password.html', form=form)
    else:
        token = PasswordToken.query.filter(PasswordToken.url_part == url_part).first()
        user = token.user
        user.password = token.hashed_password
        user.activated = True
        dbs.add(user)
        dbs.commit()
        flash('New password confirmed, please login below', 'alert alert-success')
        return redirect(url_for('login'))


@app.route('/user/activate/<url_part>')
def activate(url_part):

    token = ActivationToken.query.filter(ActivationToken.url_part == url_part).first()
    
    if token is not None:
        user = token.user
        user.activated = True
        dbs.add(user)
        dbs.commit()

        flash('Account activated, please login.', 'alert alert-success')
        return redirect(url_for('login'))
    else:
        return 'Failure'


@app.route('/buy/', methods=['GET', 'POST'])
@login_required
def buy():
    if request.method == 'POST':
        user = User.get(session['email'])
        item = Item.query.filter(Item.id == request.form['item_id']).first()
        purchase = Purchase(user, item)
        dbs.add(purchase)
        dbs.commit()
        flash('Purchase successful, return to buy.', 'alert alert-success')
        return redirect(url_for('history'))
    else:
        data = {
            'nav_urls': get_urls(),
            'active_url': url_for('buy')
        }

        data['items'] = Item.query.filter(Item.active)
        response = make_response(render_template('buy.html', data=data))
        response.headers['Cache-Control'] = 'no-cache'
        return response


@app.route('/history/')
@login_required
def history():
    data = {
        'nav_urls': get_urls(),
        'active_url': url_for('history')
    }
    user = User.get(session['email'])
    purchases = Purchase.query.filter(Purchase.user_id == user.id).order_by(Purchase.timestamp.desc())
    payments = Payment.query.filter(Payment.user_id == user.id).order_by(Payment.timestamp.desc())

    balance = 0

    for purchase in purchases:
        balance -= purchase.price

    for payment in payments:
        balance += payment.value

    data['purchases'] = purchases
    return render_template('history.html', data=data, payments=payments, balance=balance)


@app.route('/items/')
@login_required
@group_required(['admin'])
def items():
    data = {
        'nav_urls': get_urls(),
        'active_url': url_for('items'),
        'items': Item.query.all()
    }
    return render_template('items.html', data=data)


@app.route('/items/new/', methods=['GET', 'POST'])
@login_required
@group_required(['admin'])
def items_new():
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        if Item.query.filter(Item.name == form.name.data).first():
            data = {
                'nav_urls': get_urls(),
                'active_url': url_for('items_new')
            }
            duplicate = True
            return render_template('items_edit.html', form=form, data=data, duplicate=duplicate)
        else:
            item = Item(form.name.data, form.price.data)
            item.active = form.active.data
            dbs.add(item)
            dbs.commit()
            return redirect(url_for('items'))
    else:
        data = {
            'nav_urls': get_urls(),
            'active_url': url_for('items_new')
        }
        return render_template('items_edit.html', form=form, data=data)


@app.route('/items/edit/<item_id>/', methods=['GET', 'POST'])
@login_required
@group_required(['admin'])
def items_edit(item_id):
    form = ItemForm(request.form)

    if request.method == 'POST' and form.validate():
        if Item.query.filter(Item.name == form.name.data, Item.id != form.id.data).first():
            data = {
                'nav_urls': get_urls(),
                'active_url': url_for('items_new')
            }
            duplicate = True
            return render_template('items_edit.html', form=form, data=data, duplicate=duplicate)
        else:
            item = Item.query.filter(Item.id == item_id).first()
            item.name = form.name.data
            item.price = form.price.data
            item.active = form.active.data
            dbs.add(item)
            dbs.commit()
            return redirect(url_for('items'))
    else:
        data = {
            'nav_urls': get_urls(),
            'active_url': url_for('items_edit', item_id=item_id)
        }
        item = Item.query.filter(Item.id == item_id).first()
        form.id.data = item.id
        form.name.data = item.name
        form.price.data = item.price
        form.active.data = item.active
        return render_template('items_edit.html', data=data, form=form)


@app.route('/payment/', methods=['GET', 'POST'])
@login_required
@group_required(['admin'])
def payment():
    form = PaymentForm(request.form)
    users = User.query.filter(User.activated).order_by(User.email.asc())

    if request.method == 'POST' and form.validate():
        user = User.query.filter(User.id == request.form['user_id']).first()
        payment = Payment(user, form.value.data)
        dbs.add(payment)
        dbs.commit()
        flash('Payment added successfully.', 'alert alert-success')
        return redirect(url_for('payment'))
    else:
        data = {
            'nav_urls': get_urls(),
            'active_url': url_for('payment')
        }
        return render_template('payment_add.html', data=data, form=form, users=users)


@app.route('/admin/users/')
@login_required
@group_required(['admin'])
def users():
    users = User.query.all()
    render_users = []

    for user in users:
        purchases = Purchase.query.filter(Purchase.user_id == user.id).order_by(Purchase.timestamp.desc())
        payments = Payment.query.filter(Payment.user_id == user.id).order_by(Payment.timestamp.desc())

        balance = 0

        for purchase in purchases:
            balance -= purchase.price

        for payment in payments:
            balance += payment.value

        render_users.append((user.email, balance))

    render_users.sort()
    data = {
        'nav_urls': get_urls(),
        'active_url': url_for('users')
    }
    return render_template('users.html', data=data, users=render_users)


@app.route('/buy/quick/', methods = ['GET', 'POST'])
def quick_buy():

    users = User.query.filter(User.activated).order_by(User.email.asc())
    items = Item.query.filter(Item.active)

    if request.method == 'POST':
        user = User.query.filter(User.id == request.form['user_id']).first()

        if user is not None and Authentication.authenticate(user, request.form['password']):
            item = Item.query.filter(Item.id == request.form['item_id']).first()
            purchase = Purchase(user, item)
            dbs.add(purchase)
            dbs.commit()
            flash('Quick-buy successful!', 'alert alert-success')
        else:
            flash('Quick-buy failed, please try again with the right password.', 'alert alert-danger')

    return render_template('quick_buy.html', users=users, items=items)


if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')
    app.run()
