
from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, loader_manager
from app.forms import *
from app.models import Users, Tree, Branch
from flask.ext.login import login_user, logout_user, current_user, login_required

@loader_manager.user_loader
def load_user(user_id):
  return Users.query.filter_by(id=user_id).first()

@app.route('/index')
@app.route('/about')
def about():
  return render_template("about.html",
                          title = 'About',
                          user = g.user)

# registration
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
  if g.user is not None and g.user.is_authenticated():
    return redirect(url_for('about'))
  form = SignupForm(request.form)
  if request.method == "POST" and form.validate():
    return registrate(form.email.data,
             form.nickname.data,
             form.passwd.data,
             form.passwd_chk.data)
  return render_template('signup.html',
                          title = 'Sign Up',
                          form = form)

@app.route('/success_signup')
def success_signup():
  return render_template("success_signup.html",
                          title = 'Success')

def registrate(email, nickname, passwd, passwd_chk):
  email_splitted = email.split('@')
  if len(email_splitted) != 2:
    flash('Email address isn\'t correct. Try again')
    return redirect(url_for('signup'))
  if nickname == '':
    nickname = email_splitted[0]

  if Users.query.filter_by(nickname = nickname).first() is not None:
    flash('The user with such nickname already exist. Try another nickname')
    return redirect(url_for('signup'))

  if passwd != passwd_chk:
    flash('The passwords don\'t match. Try again')
    return redirect(url_for('signup'))

  user = Users.query.filter_by(email = email).first()
  if user is not None:
    flash('The user with such email already exist. Try another email')
    return redirect(url_for('signup'))
  else:
    user = Users(email = email, nickname = nickname, passwd = passwd)
    user.set_password(passwd)
    db.session.add(user)
    firstTree = Tree(user, "firstTree")

    # for tests
    rootb = firstTree.rootb
    b1 = Branch(text="branch1_" + str(firstTree.name), parent=rootb)
    b11 = Branch(text="branch11_" + str(firstTree.name), parent=b1)
    b12 = Branch(text="branch12_" + str(firstTree.name), parent=b1)
    #

    db.session.commit()
    return redirect(url_for('success_signup'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if g.user is not None and g.user.is_authenticated():
    return redirect(url_for('about'))
  form = LoginForm(request.form)
  if request.method == "POST" and form.validate():
    session['remember_me'] = form.remember_me.data
    return auth(form.email_nickname.data,
          form.passwd.data)
  return render_template('login.html',
              title = 'Log In',
              form = form)

def auth(email_nickname, passwd):
  user = Users.query.filter_by(email = email_nickname).first()
  if user is None:
   user = Users.query.filter_by(nickname = email_nickname).first()

  if user is None or not user.check_password(passwd):
    flash('Invalid login or password. Please try again.')
    return redirect(url_for('login'))
  remember_me = False
  if 'remember_me' in session:
    remember_me = session['remember_me']
    session.pop('remember_me', None)
  login_user(user, remember = remember_me)
  return redirect(request.args.get('next') or url_for('tree'))

@app.route('/user')
@login_required
def user():
  user = g.user
  return render_template("user.html",
                       user=user)

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for('about'))

@app.route('/removeuser')
@login_required
def removeuser():
  user = g.user
  db.session.delete(user)
  db.session.commit()
  return redirect(url_for('about'))

@app.before_request
def before_request():
  g.user = current_user


def for_test():
  Forest().remove()
  Users().removeAll()

  alex = Users("Alex", "123", "alex@gmail.com")
  bob = Users("Bob", "123456", "bob@gmail.com")

  testTree1 = Tree(alex, "testTree1")
  testTree2 = Tree(alex, "testTree2")
  testTree3 = Tree(bob, "testTree3")
  testTree4 = Tree(alex, "testTree4")

  for curT in Forest().allTrees():
    rootb = curT.rootb
    b1 = Branch(text="branch1_" + str(curT.name), parent=rootb)
    b11 = Branch(text="branch11_" + str(curT.name), parent=b1)
    b12 = Branch(text="branch12_" + str(curT.name), parent=b1)

    b2 = Branch(text="branch2_" + str(curT.name), main=True, parent=rootb)
    b21 = Branch(text="branch21_" + str(curT.name), parent=b2)

    b3 = Branch(text="branch3_" + str(curT.name), main=True, parent=rootb)
    b31 = Branch(text="branch31_" + str(curT.name), parent=b3)

def getList_subbsOf(branch, nestedocs_mode = False):
  """
  getList of subbranches of "branch" in format for jstree
  nestedocs_mode:
    == True   --output not main branches only
    == False  --output main branches only
  """
  def getDict(branch):
    if nestedocs_mode :
      if branch.main:
        return None
    else:
      if not branch.main :
        return None

    dict = {}
    dict['id'] = branch.id
    dict['text'] = branch.text

    if branch.get_subbs() != [] :
      dict['state'] = {}
      dict['state']['opened'] = branch.folded ^ True
      if dict['state']['opened'] == True:
        dict['children'] = []
        for cur_subb in branch.get_subbs():
          newchild = getDict(branch = cur_subb)
          if newchild :
            dict['children'].append(newchild)
      else:
        dict['children'] = True
    return dict

  list = []
  subbs = branch.get_subbs()
  if len(subbs):
    for cur_subb in subbs:
      newsubb = getDict(cur_subb)
      if newsubb :
        list.append(newsubb)
  return list


@app.route('/')
@app.route('/tree')
@login_required
def tree():
  user = g.user
  return render_template("tree.html",
                       user=user)

import json
@app.route('/mngtree', methods = ['GET', 'POST'])
@login_required
def mngtree():
  user = g.user

  #for_test()

  if request.method == "GET":
    curtree_id = request.args.get('tree_id', default=user.get_latestTree().id, type=int)
    curtree = user.getTree(curtree_id)

    import app.general
    nestedocs = app.general.str2bool(request.args.get('nestedocs', default='False', type=str))
    cmd = request.args.get('cmd', default='', type=str)
    id = request.args.get('id', default='', type=str)

    # after integration with flask symbole '%' has started to add to id. So we need to remove it
    if id[:1] == "%":
      id = int(id[1:])
    if id == '#' or id == None:
      id = curtree.rootb_id

  else:
    form = SaveDataForm(request.form)
    if request.method == "POST" and form.validate():
      curtree_id = form.curtree_id.data
      if curtree_id == -1:
        curtree_id = user.get_latestTree().id
      curtree = user.getTree(curtree_id)

      nestedocs = form.nestedocs.data
      cmd = form.cmd.data
      id = form.id.data
      data = form.data.data

  """
  cmd = "load_subbs"
  id = 4
  id = '#'
  """

  if cmd != "" :
    if cmd == "fold":
      b = curtree.getB(id)
      b.folded = True
    elif cmd == "unfold":
      b = curtree.getB(id)
      b.folded = False
    elif cmd == "rename_node":
      data = request.args.get('data', default='', type=str)
      curtree.getB(id).text = data
    elif cmd == "move_node":
      b = curtree.getB(id)
      new_parent_id = request.args.get('new_parent', default=curtree.rootb_id, type=int)
      position = request.args.get('position', default=-1, type=int)
      b.move(new_parent_id, position)
    else:
      if not nestedocs :
        if cmd == "load_subbs":
          return json.dumps(getList_subbsOf(curtree.getB(id), nestedocs))
          #curtree.set_latestB(id)
        if cmd == "load_data":
          return curtree.getB(id).text
        if cmd == "create_node":
          parent_id = request.args.get('parent_id', default=curtree.rootb_id, type=int)
          parentB = curtree.getB(parent_id)
          newB = Branch(main = True, parent_id = parent_id)
          return str( newB.id )
        if cmd == "delete_node":
          branch = curtree.getB(id)
          branch.remove()
      else:
        if cmd == "load_subbs":
          return json.dumps(getList_subbsOf(curtree.getB(id), nestedocs))
        if cmd == "load_data":
          return curtree.getB(id).text
        if cmd == "save_data":
          curtree.getB(id).text = data
        if cmd == "create_node":
          parent_id = request.args.get('parent_id', default=curtree.rootb_id, type=int)
          parentB = curtree.getB(parent_id)
          newB = Branch(main = False, parent_id = parent_id)
          return str( newB.id )
        if cmd == "delete_node":
          branch = curtree.getB(id)
          branch.remove()
  db.session.commit()
  return ""


"""
@app.route('/test')
def test():
  print("\ntest\n")
"""
