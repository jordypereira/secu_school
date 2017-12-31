from flask import Blueprint, render_template, flash, redirect, url_for, logging, request, session
from ..extensions import mysql
from functools import wraps
from ..forms import KlasForm

klas = Blueprint('klas', __name__, template_folder='../templates/klas')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please login", 'danger')
            return redirect(url_for('dashboard.login'))
    return wrap

# Add Klas
@klas.route('/add_klas', methods=['GET', 'POST'])
@is_logged_in
def add_klas():

    form = KlasForm()

    cur = mysql.connection.cursor()

    cur.execute('SELECT id, naam FROM richtingen')
    richtingen = cur.fetchall()
    cur.execute('SELECT id, naam, voornaam FROM leraren')
    leraren = cur.fetchall()

    if form.validate_on_submit():
        naam = form.naam.data
        code = form.code.data
        richting = request.form['richting']
        leraar = request.form['leraar']

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO klassen(naam, code, richting, leraar) VALUES(%s, %s, %s, %s)",(naam, code, richting, leraar))

        mysql.connection.commit()

        cur.close()

        flash('Klas Aangemaakt', 'success')

        return redirect(url_for('dashboard.intranet'))
    return render_template('add_klas.html', form=form, richtingen = richtingen, leraren = leraren)
    cur.close()

# Edit Klas
@klas.route('/edit_klas/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_klas(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    cur.execute('SELECT * FROM klassen WHERE id=%s', [id])
    klas = cur.fetchone()

    cur.execute('SELECT id, naam FROM richtingen')
    richtingen = cur.fetchall()

    cur.execute('SELECT id, naam, voornaam FROM leraren')
    leraren = cur.fetchall()

    # Get form
    form = KlasForm()

    # Populate article form fields
    form.naam.data = klas['naam']
    form.code.data = klas['code']


    if form.validate_on_submit():
        naam = request.form['naam']
        omschrijving = request.form['omschrijving']

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE richtingen SET naam=%s, omschrijving=%s WHERE id = %s", (naam, omschrijving, id))

        mysql.connection.commit()

        cur.close()

        flash('Richting Updated', 'success')

        return redirect(url_for('dashboard.intranet'))

    return render_template('edit_klas.html', form=form, klas=klas, richtingen=richtingen, leraren=leraren)
