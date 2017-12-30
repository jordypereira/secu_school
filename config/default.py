UPLOAD_FOLDER = 'static/images/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DEBUG = False
# Config MySQL
app.config['MYSQL_DB'] = 'secu_school'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
set FLASK_APP=views
set FLASK_DEBUG=true
