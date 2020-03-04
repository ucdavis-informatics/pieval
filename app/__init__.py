from flask import Flask, Blueprint

# CREATE APP OBJECT
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

# import the code that actually executes app functions
from app import pieval
app.register_blueprint(pieval.bp, url_prefix=app.config['BLUEPRINT_URL_PREFIX'])
# app config
app.secret_key = app.config['SECRET_KEY']
