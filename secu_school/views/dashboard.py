from flask import Blueprint, current_app, render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from ..forms import RegisterForm, LoginForm
from passlib.hash import sha256_crypt
from functools import wraps
from os.path import join
from os import remove

from werkzeug.utils import secure_filename
from ..extensions import mysql


dashboard = Blueprint('dashboard', __name__, template_folder='../templates/dashboard', static_folder="../static")


# Return upload folder
@dashboard.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    filename = folder + "/" + filename
    return send_from_directory("static/images/", filename)


# User Register
@dashboard.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, password) VALUES(%s, %s, %s)", (name, email, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Je account is geregistreerd in de database en je kan nu inloggen.', 'success')

        return redirect(url_for('dashboard.login'))

    return render_template('register.html', form=form)

# Login
@dashboard.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password_candidate = form.password.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Get User by username
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            name = data['name']

            # Compare pw
            if sha256_crypt.verify(password_candidate, password):
                # Logged in
                session['logged_in'] = True
                session['email'] = email
                session['name'] = name

                flash('Je bent nu ingelogd.', 'success')
                return redirect(url_for('dashboard.intranet'))
            else:
                error = 'Foute login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Email niet gevonden'
            return render_template('login.html', error=error)

    return render_template('login.html', form=form)

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

# Logout
@dashboard.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('dashboard.login'))

# Delete Row
@dashboard.route('/deleteRow/<string:table>/<string:id>/<string:name>', methods=['POST'])
@is_logged_in
def deleteRow(table, id, name):
    # Create Cursor
    cur = mysql.connection.cursor()

    if table == 'leraren':
        cur.execute("SELECT foto FROM %s WHERE id = %s"%(table, id))
        filename = cur.fetchone()
        deleteFile(table, filename['foto'])
    # Execute
    cur.execute("DELETE FROM %s WHERE id = %s"%(table, id))

    mysql.connection.commit()

    cur.close()

    flash('%s verwijderd'%(name), 'success')

    return redirect(url_for('dashboard.intranet'))

def deleteFile(folder, filename):
    filename = folder + "/" + filename
    return remove(join(current_app.config['UPLOAD_FOLDER'], filename))

# Intranet
@dashboard.route('/intranet')
@is_logged_in
def intranet():
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM richtingen')
    richtingen = cur.fetchall()
    cur.execute('SELECT * FROM leraren')
    leraren = cur.fetchall()
    cur.execute('''SELECT klassen.id, klassen.naam, klassen.code, CONCAT(leraren.voornaam, ' ' ,leraren.naam) AS leraar, richtingen.naam AS richting FROM klassen INNER JOIN leraren ON klassen.leraar = leraren.id INNER JOIN richtingen ON klassen.richting = richtingen.id''')
    klassen = cur.fetchall()

    return render_template('intranet.html', richtingen=richtingen, leraren=leraren, klassen=klassen)
    cur.close()
