from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

from .views.home import home
from .views.dashboard import dashboard
from .views.klas import klas
from .views.richting import richting

app = Flask(__name__, instance_relative_config=True)
app.register_blueprint(home)
app.register_blueprint(dashboard)
app.register_blueprint(klas)
app.register_blueprint(richting)

app.config.from_object('config.default')
app.config.from_pyfile('config.py')
app.config.from_object('config.development')
