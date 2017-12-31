from flask import Flask, render_template, session
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from .extensions import mysql

app = Flask(__name__, instance_relative_config=True) # , instance_relative_config=True

app.config.from_object('config.default')
app.config.from_pyfile('config.py')
app.config.from_object('config.development')

# import secu_school.views
from .views.home import home
from .views.dashboard import dashboard
from .views.klas import klas
from .views.richting import richting

app.register_blueprint(home)
app.register_blueprint(dashboard)
app.register_blueprint(klas)
app.register_blueprint(richting)

# init MySQL
mysql.init_app(app)

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['SECRET_KEY'] = 'secret123'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://secu_webmaster:123456@localhost/spaceshipDB"
# app.config['UPLOAD_FOLDER'] = 'static/images/'
# # Config MySQL
# app.config['MYSQL_DB'] = 'secu_school'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# if __name__ == '__main__':
#      app.run(debug=True)
