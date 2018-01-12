from flask import Blueprint, render_template, request, abort, flash, redirect, url_for, make_response, request, session
from jinja2 import TemplateNotFound
from ..forms import ContactForm
from wtforms import StringField, TextAreaField, PasswordField, Form, validators
from ..extensions import mysql
import time


home = Blueprint('home', __name__, template_folder='../templates/home/')

# Index
@home.route('/')
def index():
    resp = request.cookies.get('visited')
    timestamp = None

    t = time.strftime("%H:%M:%S")
    (h, m, s) = t.split(':')
    result = int(h) * 3600 + int(m) * 60 + int(s)

    if 0 <= result < 43200:
        timestamp = 'Goedemorgen'
    elif 43200 <= result < 64800:
        timestamp = 'Goedemiddag'
    elif 64800 <= result:
        timestamp = 'Goedeavond'

    if resp:
        text = "Welkom terug"
    else:
        text= "Welkom"
        resp = make_response(render_template('home.html', text=text))
        resp.set_cookie('visited', 'true')
        return resp
    return render_template('home.html', text=text, time=timestamp)

# Ons Aanbod
@home.route('/aanbod')
def aanbod():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM richtingen')
    richtingen = cur.fetchall()

    if result > 0:
        return render_template('aanbod.html', richtingen = richtingen)
    else:
        msg = 'Geen richtingen in het systeem.'
        try:
            return render_template('home/aanbod.html', msg=msg)
        except TemplateNotFound:
            abort(404)
    cur.close()

# Wie is Wie
@home.route('/wieiswie')
def wieiswie():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM leraren')
    leraren = cur.fetchall()

    if result > 0:
        return render_template('wieiswie.html', leraren = leraren)
    else:
        msg = 'Geen leerkrachten in het systeem.'
        return render_template('wieiswie.html', msg=msg)
    cur.close()

# Contact
@home.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        naam = form.naam.data
        email = form.email.data
        onderwerp = form.onderwerp.data
        bericht = form.bericht.data

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO contact(naam, email, onderwerp, bericht) VALUES(%s, %s, %s, %s)", (naam, email, onderwerp, bericht))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Je bericht is verstuurd', 'success')

        return redirect(url_for('home.contact'))

    return render_template('contact.html', form=form)

@home.after_app_request
def store_visited_urls(response):
    if 'urls' in session:
        session['urls'].append(request.url)
        session.modified = True
    # if len[session['urls']] > 5:
    #     session['urls'].pop(0)
    return response
