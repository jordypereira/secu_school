from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length


# Klas Form Class
class KlasForm(FlaskForm):
    naam = StringField('Naam', validators=[DataRequired()])
    code = StringField('Code', validators=[DataRequired()])

# Login Form Class
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

# Register Form Class
class RegisterForm(FlaskForm):
    name = StringField('Naam', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

# Leraren Form Class
class LeraarForm(FlaskForm):
    naam = StringField('Naam', validators=[Length(min=1, max=200)])
    voornaam = StringField('Voornaam', validators=[Length(min=1, max=200)])
    email = StringField('Email', validators=[DataRequired()])

# Contact Form Class
class ContactForm(FlaskForm):
    naam = StringField('Naam', validators=[Length(min=1, max=50)])
    email = StringField('Email', validators=[Length(min=6, max=50), Email()])
    onderwerp = StringField('Onderwerp', validators=[Length(min=1, max=255)])
    bericht = TextAreaField('Bericht', validators=[Length(min=30)])


# Richting Form Class
class RichtingForm(FlaskForm):
    naam = StringField('Naam', validators=[Length(min=1, max=200)])
    omschrijving = TextAreaField('Omschrijving', validators=[Length(min=1)])
