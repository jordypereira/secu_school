import os
from secu_school import app
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps

from wtforms import StringField, TextAreaField, PasswordField, Form, validators
from wtforms.validators import DataRequired

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# init MySQL
mysql = MySQL(app)

# Return upload folder
@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    filename = folder + "/" + filename
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Index
@app.route('/')
def index():
    return render_template('home.html')

# Ons Aanbod
@app.route('/aanbod')
def aanbod():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM richtingen')
    richtingen = cur.fetchall()

    if result > 0:
        return render_template('aanbod.html', richtingen = richtingen)
    else:
        msg = 'Geen richtingen in het systeem.'
        return render_template('aanbod.html', msg=msg)
    cur.close()

# Wie is Wie
@app.route('/wieiswie')
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

# Contact Form Class
class ContactForm(Form):
    naam = StringField('Naam', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    onderwerp = StringField('Onderwerp', [validators.Length(min=1, max=255)])
    bericht = TextAreaField('Bericht', [validators.Length(min=30)])

# Contact
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
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

        return redirect(url_for('contact'))

    return render_template('contact.html', form=form)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Naam', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
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

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

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
                return redirect(url_for('intranet'))
            else:
                error = 'Foute login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Email niet gevonden'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please login", 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Intranet
@app.route('/intranet')
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

# Richting Form Class
class RichtingForm(Form):
    naam = StringField('Naam', [validators.Length(min=1, max=200)])
    omschrijving = TextAreaField('Omschrijving', [validators.Length(min=1)])

# Add Richting
@app.route('/add_richting', methods=['GET', 'POST'])
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
@app.route('/edit_richting/<string:id>', methods=['GET', 'POST'])
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

# Leraren Form Class
class LeraarForm(Form):
    naam = StringField('Naam', [validators.Length(min=1, max=200)])
    voornaam = StringField('Voornaam', [validators.Length(min=1, max=200)])

# Check the file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add Leraren
@app.route('/add_leraar', methods=['GET', 'POST'])
@is_logged_in
def add_leraar():
    form = LeraarForm(request.form)
    if request.method == 'POST' and form.validate():
         # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        filename = file.filename
        naam = form.naam.data
        voornaam = form.voornaam.data
        email = request.form['email']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # UPLOAD TO DB
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'leraren/' + filename))
            # Create cursor
            cur = mysql.connection.cursor()

            cur.execute("INSERT INTO leraren(foto, naam, voornaam, email) VALUES(%s, %s, %s, %s)", (filename, naam, voornaam, email))

            mysql.connection.commit()

            cur.close()

            flash('Leerkracht Toegevoegd', 'success')

            return redirect(url_for('intranet'))

    return render_template('add_leraar.html', form=form)


# Edit Leraren
@app.route('/edit_leraar/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_leraar(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute('SELECT * FROM leraren WHERE id=%s', [id])

    leraar = cur.fetchone()

    # Get form
    form = LeraarForm(request.form)

    # Populate leraar form fields
    form.naam.data = leraar['naam']
    form.voornaam.data = leraar['voornaam']
    form.email.data = leraar['email']

    if request.method == 'POST' and form.validate():
        naam = request.form['naam']
        voornaam = request.form['voornaam']
        email = request.form['email']

         # check if the post request has the file part
        if 'file' not in request.files:
            # Update db
            cur = mysql.connection.cursor()

            cur.execute("UPDATE leraren SET naam=%s, voornaam=%s, email=%s WHERE id = %s", (naam, voornaam, email, id))

            mysql.connection.commit()

            cur.close()

        file = request.files['file']
        filename = file.filename

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # Update db
            cur = mysql.connection.cursor()

            cur.execute("UPDATE leraren SET naam=%s, voornaam=%s, email=%s WHERE id = %s", (naam, voornaam, email, id))

            mysql.connection.commit()

            cur.close()

        # UPLOAD TO DB
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'leraren/' + filename))

            # Update db
            cur = mysql.connection.cursor()

            cur.execute("SELECT foto FROM leraren WHERE id = %s"%(id))
            old_filename = cur.fetchone()
            deleteFile("leraren", old_filename['foto'])

            cur.execute("UPDATE leraren SET naam=%s, voornaam=%s, foto=%s, email=%s WHERE id = %s", (naam, voornaam, filename, email, id))

            mysql.connection.commit()

            cur.close()

        flash('Leraar Updated', 'success')

        return redirect(url_for('intranet'))
    return render_template('edit_leraar.html', form=form)

# Klas Form Class
class KlasForm(Form):
    naam = StringField('Naam', [validators.Length(min=1, max=200)])
    code = StringField('Code', [validators.Length(min=1, max=200)])

# Add Klas
@app.route('/add_klas', methods=['GET', 'POST'])
@is_logged_in
def add_klas():

    form = KlasForm(request.form)

    cur = mysql.connection.cursor()

    cur.execute('SELECT id, naam FROM richtingen')
    richtingen = cur.fetchall()
    cur.execute('SELECT id, naam, voornaam FROM leraren')
    leraren = cur.fetchall()

    if request.method == "POST" and form.validate():
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

        return redirect(url_for('intranet'))
    return render_template('add_klas.html', form=form, richtingen = richtingen, leraren = leraren)
    cur.close()

# Edit Klas
@app.route('/edit_klas/<string:id>', methods=['GET', 'POST'])
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
    form = KlasForm(request.form)

    # Populate article form fields
    form.naam.data = klas['naam']
    form.code.data = klas['code']


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

    return render_template('edit_klas.html', form=form, klas=klas, richtingen=richtingen, leraren=leraren)

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        mysql.connection.commit()

        cur.close()

        flash('Article created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute('SELECT * FROM articles WHERE id=%s', [id])

    article = cur.fetchone()

    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))

        mysql.connection.commit()

        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

# Delete Row
@app.route('/deleteRow/<string:table>/<string:id>/<string:name>', methods=['POST'])
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

    return redirect(url_for('intranet'))


def deleteFile(folder, filename):
    filename = folder + "/" + filename
    return os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
