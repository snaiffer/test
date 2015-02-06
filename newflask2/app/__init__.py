
from flask import Flask
#from flask_wtf.csrf import CsrfProtect
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
#CsrfProtect(app)
app.config.from_object('config')
db = SQLAlchemy(app)

import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import views, models
