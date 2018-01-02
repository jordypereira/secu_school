from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension

csrf = CSRFProtect()
mysql = MySQL()
toolbar = DebugToolbarExtension()
