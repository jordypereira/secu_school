from flask import Blueprint, render_template, flash, redirect, url_for, logging, request, session
from ..forms import RichtingForm
from ..extensions import mysql
from functools import wraps

richting = Blueprint('richting', __name__, template_folder='../templates/richting')


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

# Add Richting
@richting.route('/add_richting', methods=['GET', 'POST'])
@is_logged_in
def add_richting():

    form = RichtingForm()

    if form.validate_on_submit():
        naam = form.naam.data
        omschrijving = form.omschrijving.data

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO richtingen(naam, omschrijving) VALUES(%s, %s)",(naam, omschrijving))

        mysql.connection.commit()

        cur.close()

        flash('Richting Aangemaakt', 'success')

        return redirect(url_for('dashboard.intranet'))
    return render_template('add_richting.html', form=form)

# Edit Richting
@richting.route('/edit_richting/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_richting(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute('SELECT * FROM richtingen WHERE id=%s', [id])

    richting = cur.fetchone()

    # Get form
    form = RichtingForm()

    # Populate article form fields
    form.naam.data = richting['naam']
    form.omschrijving.data = richting['omschrijving']

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
    return render_template('edit_richting.html', form=form)
