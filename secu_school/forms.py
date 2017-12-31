from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length


# Klas Form Class
class KlasForm(Form):
    naam = StringField('Naam', validators=[DataRequired()])
    code = StringField('Code', validators=[DataRequired()])

# Register Form Class
class RegisterForm(Form):
    name = StringField('Naam', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

# Leraren Form Class
class LeraarForm(Form):
    naam = StringField('Naam', validators=[Length(min=1, max=200)])
    voornaam = StringField('Voornaam', validators=[Length(min=1, max=200)])

# Contact Form Class
class ContactForm(Form):
    naam = StringField('Naam', validators=[Length(min=1, max=50)])
    email = StringField('Email', validators=[Length(min=6, max=50), Email()])
    onderwerp = StringField('Onderwerp', validators=[Length(min=1, max=255)])
    bericht = TextAreaField('Bericht', validators=[Length(min=30)])
