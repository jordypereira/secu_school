from flask import Blueprint, render_template, flash, redirect, url_for, logging, request, current_app
from ..forms import LeraarForm
from os.path import join
from ..extensions import mysql
from ..helpers import deleteFile, is_logged_in, allowed_file
from werkzeug.utils import secure_filename



leraar = Blueprint('leraar', __name__, template_folder='../templates/leraar')


# Add Leraren
@leraar.route('/add_leraar', methods=['GET', 'POST'])
@is_logged_in
def add_leraar():
    form = LeraarForm()
    if form.validate_on_submit():
         # check if the post request has the file part
        if 'file' not in request.files:
            flash('Geen foto gevonden.', 'danger')
            return redirect(request.url)

        file = request.files['file']
        filename = file.filename
        naam = form.naam.data
        voornaam = form.voornaam.data
        email = request.form['email']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('Geen foto geselecteerd')
            return redirect(request.url)

        # UPLOAD TO DB
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(join(current_app.config['UPLOAD_FOLDER'], 'leraren/' + filename))
            # Create cursor
            cur = mysql.connection.cursor()

            cur.execute("INSERT INTO leraren(foto, naam, voornaam, email) VALUES(%s, %s, %s, %s)", (filename, naam, voornaam, email))

            mysql.connection.commit()

            cur.close()

            flash('Leerkracht Toegevoegd', 'success')

            return redirect(url_for('dashboard.intranet'))

    return render_template('add_leraar.html', form=form)


# Edit Leraren
@leraar.route('/edit_leraar/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_leraar(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute('SELECT * FROM leraren WHERE id=%s', [id])

    leraar = cur.fetchone()

    # Get form
    form = LeraarForm()

    # Populate leraar form fields
    form.naam.data = leraar['naam']
    form.voornaam.data = leraar['voornaam']
    form.email.data = leraar['email']


    if form.validate_on_submit():
        naam = request.form['naam']
        voornaam = request.form['voornaam']
        email = request.form['email']

         # check if the post request has the file part
        if 'file' not in request.files:
            # Update db
            cur = mysql.connection.cursor()

            cur.execute("UPDATE leraren SET naam=%s, voornaam=%s, email=%s WHERE id = %s", (naam, voornaam, email, id))

            mysql.connection.commit()

            flash('Leraar Updated', 'success')

            return redirect(url_for('dashboard.intranet'))

        file = request.files['file']
        filename = file.filename

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # Update db
            cur = mysql.connection.cursor()

            cur.execute("UPDATE leraren SET naam=%s, voornaam=%s, email=%s WHERE id = %s", (naam, voornaam, email, id))

            mysql.connection.commit()

        # UPLOAD TO DB
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(join(current_app.config['UPLOAD_FOLDER'], 'leraren/' + filename))

            # Update db
            cur = mysql.connection.cursor()

            cur.execute("SELECT foto FROM leraren WHERE id = %s"%(id))
            old_filename = cur.fetchone()
            deleteFile("leraren", old_filename['foto'])

            cur.execute("UPDATE leraren SET naam=%s, voornaam=%s, foto=%s, email=%s WHERE id = %s", (naam, voornaam, filename, email, id))

            mysql.connection.commit()

        flash('Leraar Updated', 'success')

        return redirect(url_for('dashboard.intranet'))
    return render_template('edit_leraar.html', form=form, leraar=leraar)
    cur.close()
