from wtforms import Form, BooleanField, StringField, DecimalField, IntegerField, validators

class ItemForm(Form):
	id = IntegerField('ID')
	name = StringField('Name', [validators.InputRequired()])
	price = DecimalField('Price', [validators.InputRequired()], places=2, rounding=None)