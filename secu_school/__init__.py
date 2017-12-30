from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_from_directory

from .views import app

app = Flask(__name__, instance_relative_config=True)
# Load the default configuration
app.config.from_object('config.default')

# Load the configuration from the instance folder
app.config.from_pyfile('config.py')

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration
app.config.from_object('config.development')
