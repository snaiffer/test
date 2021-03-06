from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    passwd = db.Column(db.String(160), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    """
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    """

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.passwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwd, password)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


"""
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
"""
