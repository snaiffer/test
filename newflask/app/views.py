
from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, loader_manager
from app.forms import LoginForm, RegistrationForm
from app.models import Users
from flask.ext.login import login_user, logout_user, current_user, login_required

@loader_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()

@app.route('/')
@app.route('/index')
@login_required
def index():
  user = g.user
  return render_template("index.html",
                       title='Home',
                       user=user)

@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        return registrate(form.username.data,
                          form.passwd.data,
                          form.email.data)
    return render_template('registration.html',
        title = 'Sign Up',
        form = form)

@app.route('/success_registration')
def success_registration():
  return render_template("success_registration.html",
        title = 'Success')

def registrate(username, passwd, email):
    user = Users.query.filter_by(nickname = username).first()
    if user is not None:
        flash('Such user already exist. Try another username')
        return redirect(url_for('registration'))
    else:
        user = Users(nickname = username, passwd = passwd, email = email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('success_registration'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        session['remember_me'] = form.remember_me.data
        return auth(form.username.data,
                    form.passwd.data)
    return render_template('login.html',
                            title = 'Sign In',
                            form = form)

def auth(username, passwd):
    """
    if username is None or username == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    """
    user = Users.query.filter_by(nickname = username).first()
    if user is None or user.passwd != passwd:
        flash('Invalid login or password. Please try again.')
        return redirect(url_for('login'))
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/removeuser')
@login_required
def removeuser():
    user = g.user
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user = current_user

