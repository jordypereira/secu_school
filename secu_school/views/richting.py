from flask import Blueprint, render_template, flash, redirect, url_for, logging, request
from flask_mysqldb import MySQL
from wtforms import StringField, TextAreaField, Form, validators

richting = Blueprint('richting', __name__)


# Richting Form Class
class RichtingForm(Form):
    naam = StringField('Naam', [validators.Length(min=1, max=200)])
    omschrijving = TextAreaField('Omschrijving', [validators.Length(min=1)])

# Add Richting
@richting.route('/add_richting', methods=['GET', 'POST'])
@is_logged_in
def add_richting():

    form = RichtingForm(request.form)

    if request.method == "POST" and form.validate():
        naam = form.naam.data
        omschrijving = form.omschrijving.data

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO richtingen(naam, omschrijving) VALUES(%s, %s)",(naam, omschrijving))

        mysql.connection.commit()

        cur.close()

        flash('Richting Aangemaakt', 'success')

        return redirect(url_for('intranet'))
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
    form = RichtingForm(request.form)

    # Populate article form fields
    form.naam.data = richting['naam']
    form.omschrijving.data = richting['omschrijving']

    if request.method == 'POST' and form.validate():
        naam = request.form['naam']
        omschrijving = request.form['omschrijving']

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE richtingen SET naam=%s, omschrijving=%s WHERE id = %s", (naam, omschrijving, id))

        mysql.connection.commit()

        cur.close()

        flash('Richting Updated', 'success')

        return redirect(url_for('intranet'))
    return render_template('edit_richting.html', form=form)
