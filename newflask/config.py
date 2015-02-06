DEBUG = True
SECRET_KEY = 'you-will-never-guess'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost/flask'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost/flask'
