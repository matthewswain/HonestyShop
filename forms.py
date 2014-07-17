from wtforms import Form, BooleanField, StringField, DecimalField, IntegerField, PasswordField, HiddenField, validators

class ItemForm(Form):
	id = HiddenField('ID')
	name = StringField('Name', [validators.InputRequired(message='Name cannot be blank.')])
	price = DecimalField('Price', [validators.InputRequired(message='Price must be between 0.00 and 9999.99'), validators.NumberRange(min=0, max=9999, message='Price must be between 0.00 and 9999.99')], places=2, rounding=None)
	active = BooleanField('Active')


class LoginForm(Form):
	email=StringField('Email', [validators.Email(message='Please enter a valid email address.')])
	password=PasswordField('Password', [validators.InputRequired(message='Password must be eight characters or more.'), validators.Length(min=8, message='Password must be eight characters or more.')])


class PaymentForm(Form):
	value = DecimalField('Value', [validators.InputRequired(message='Value must be between 0.00 and 9999.99'), validators.NumberRange(min=0, max=9999, message='Value must be between 0.00 and 9999.99')], places=2, rounding=None)