
from flask import Flask
#from flask_wtf.csrf import CsrfProtect
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
#CsrfProtect(app)
app.config.from_object('config')
db = SQLAlchemy(app)

import os
from flask.ext.login import LoginManager
from config import basedir

loader_manager = LoginManager()
loader_manager.init_app(app)
loader_manager.login_view = 'login'

from app import views, models
