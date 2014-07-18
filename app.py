from flask import Flask, render_template, url_for, request, redirect, session, make_response, flash, get_flashed_messages
from functools import wraps
from database import session as db
from models import User, Item, Purchase, ActivationToken, PasswordToken, Payment
from forms import ItemForm, LoginForm, PaymentForm
from security import Authentication, Email
from configobj import ConfigObj


config = ConfigObj('app.config')
app = Flask(__name__)
app.secret_key = 'Development secret key.'

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
        ('Home',url_for('home')),
        ('Buy',url_for('buy')),
        ('History',url_for('history')),
        ('Logout',url_for('logout')),
    ]


@app.route('/')
@login_required
def home():
    data = {}
    data['nav_urls'] = get_urls()
    data['active_url'] = url_for('home')
    return render_template('index.html', data=data)


@app.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.get(request.form['email'])
        if user != None and Authentication.authenticate(user, request.form['password']):
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


@app.route('/register/', methods=['GET','POST'])
def register():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.get(request.form['email']) == None:
            
            user = User(request.form['email'], request.form['password'])
            db.add(user)
            db.commit()

            token = ActivationToken(user)
            db.add(token)
            db.commit()

            activation_url = url_for('activate', url_part=token.url_part)
            activation_url = config['base_url'] + activation_url
            email_body = render_template('email/register.html', activation_url=activation_url)
            
            Email.send(user.email, 'Honesty Bar - Activate Account', email_body)

            flash('Account created, please activate your account using the link in your welcome email.', 'alert alert-success')        
        else:
            flash('An account with that email address already exists, please login.', 'alert alert-warning')    

        return redirect(url_for('login'))
        
    else:
        return render_template('register.html', urls=get_urls(), form=form)


@app.route('/user/activate/<url_part>')
def activate(url_part):

    token = ActivationToken.query.filter(ActivationToken.url_part==url_part).first()
    
    if token != None:
        user = token.user
        user.activated = True
        db.add(user)
        db.commit()

        flash('Account activated, please login.', 'alert alert-success')
        return redirect(url_for('login'))
    else:
        return 'Failure'


@app.route('/buy/', methods=['GET','POST'])
@login_required
def buy():
    if request.method == 'POST':
        user = User.get(session['email'])
        item = Item.query.filter(Item.id==request.form['item_id']).first()
        purchase = Purchase(user, item)
        db.add(purchase)
        db.commit()
        flash('Purchase successful, return to buy.','alert alert-success')
        return redirect(url_for('history'))
    else:
        data = {}
        data['nav_urls'] = get_urls()
        data['active_url'] = url_for('buy')

        data['items'] = Item.query.filter(Item.active==True)
        response = make_response(render_template('buy.html', data=data))
        response.headers['Cache-Control'] = 'no-cache'
        return response


@app.route('/history/')
@login_required
def history():
    data = {}
    data['nav_urls'] = get_urls()
    data['active_url'] = url_for('history')
    user = User.get(session['email'])
    purchases = Purchase.query.filter(Purchase.user_id==user.id).order_by(Purchase.timestamp.desc())
    payments = Payment.query.filter(Payment.user_id==user.id).order_by(Payment.timestamp.desc())

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
    data = {}
    data['nav_urls'] = get_urls()
    data['active_url'] = url_for('items')
    data['items'] = Item.query.all()
    return render_template('items.html', data=data)


@app.route('/items/new/', methods=['GET','POST'])
@login_required
@group_required(['admin'])
def items_new():
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        if Item.query.filter(Item.name==form.name.data).first():
            data = {}
            data['nav_urls'] = get_urls()
            data['active_url'] = url_for('items_new')
            duplicate=True
            return render_template('items_edit.html', form=form, data=data, duplicate=duplicate)
        else:
            item = Item(form.name.data, form.price.data)
            item.active = form.active.data
            db.add(item)
            db.commit()
            return redirect(url_for('items'))
    else:
        data = {}
        data['nav_urls'] = get_urls()
        data['active_url'] = url_for('items_new')
        return render_template('items_edit.html', form=form, data=data)


@app.route('/items/edit/<item_id>/', methods=['GET','POST'])
@login_required
@group_required(['admin'])
def items_edit(item_id):
    form = ItemForm(request.form)

    if request.method == 'POST' and form.validate():
        if Item.query.filter(Item.name==form.name.data, Item.id!=form.id.data).first():
            data = {}
            data['nav_urls'] = get_urls()
            data['active_url'] = url_for('items_new')
            duplicate=True
            return render_template('items_edit.html', form=form, data=data, duplicate=duplicate)
        else:
            item = Item.query.filter(Item.id==item_id).first()
            item.name = form.name.data
            item.price = form.price.data
            item.active = form.active.data
            db.add(item)
            db.commit()
            return redirect(url_for('items'))
    else:
        data = {}
        data['nav_urls'] = get_urls()
        data['active_url'] = url_for('items_edit', item_id=item_id)
        item = Item.query.filter(Item.id==item_id).first()
        form.id.data = item.id
        form.name.data = item.name
        form.price.data = item.price
        form.active.data = item.active
        return render_template('items_edit.html', data=data, form=form)


@app.route('/payment/', methods=['GET','POST'])
@login_required
@group_required(['admin'])
def payment():
    form = PaymentForm(request.form)
    users = User.query.filter(User.activated==True).order_by(User.email.asc())

    if request.method == 'POST' and form.validate():
        user = User.query.filter(User.id==request.form['user_id']).first()
        payment = Payment(user, form.value.data)
        db.add(payment)
        db.commit()
        flash('Payment added successfully.','alert alert-success')
        return redirect(url_for('payment'))
    else:
        data = {}
        data['nav_urls'] = get_urls()
        data['active_url'] = url_for('payment')
        return render_template('payment_add.html', data=data, form=form, users=users)



@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    #app.run()
