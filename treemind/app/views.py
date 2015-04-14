
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from app import app, db, loader_manager
from app.forms import *
from app.models import Users, Tree, Branch
from flask.ext.login import login_user, logout_user, current_user, login_required
import json

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
                          user = g.user,
                          form = form)

@app.route('/success_signup')
def success_signup():
  return render_template("success_signup.html",
                          title = 'Success sign up',
                          user = g.user)

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
                          user = g.user,
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
  return redirect(request.args.get('next') or url_for('trees'))

@app.route('/user')
@login_required
def user():
  user = g.user
  return render_template("user.html",
                          title = 'Account page',
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
  user = Users.getUser(email=user.email)
  user.remove()
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

def getList_subbsOf(branch, nestedocs_mode = False, withReadLabel = False):
  """
  getList of subbranches of "branch" in format for jstree
  nestedocs_mode:
    == True   --output not main branches only
    == False  --output main branches only
  withReadLabel   -- output branches with "read field" == True
  """
  def getDict(branch):
    nonlocal withReadLabel

    if nestedocs_mode :
      if branch.main:
        return None
    else:
      if not branch.main :
        return None

    if withReadLabel:
      if not branch.read :
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
def main_page():
  if g.user.is_authenticated():
    return redirect(url_for('tree'))
  else:
    return redirect(url_for('about'))

@app.route('/trees/<tree_name>')
@app.route('/trees/latesttree')
@login_required
def tree(tree_name=None):
  user = g.user
  if tree_name == None or tree_name == '':
    tree_name = user.get_latestTree().name

  tree = user.getTree(name=tree_name)
  if tree == None:
      return ""
  return render_template("tree.html",
                          title='Tree',
                          curtree=tree,
                          trees=user.allTrees(),
                          user=user,
                          latestUsedB=tree.get_latestB().id)

@app.route('/<user_name>/<tree_name>/<int:branch_id>')
def showBranch_byPath(user_name=None, tree_name=None, branch_id=None):
  user = None
  trees = None
  if g.user is not None and g.user.is_authenticated():
    user = g.user
    trees = user.allTrees()

  tree_owner = Users.getUser(nickname = user_name)
  if tree_owner != None:
    tree = tree_owner.getTree(name=tree_name)
    if tree != None:
      branch = tree.getB(branch_id)
      if branch != None:
        return render_template("tree.html",
                                title='Tree',
                                curtree=tree,
                                trees=trees,
                                user=user,
                                latestUsedB=branch.id)
  flash("Can't find the branch by current path")
  return render_template("base.html")

@app.route('/trees')
@login_required
def trees():
  user = g.user
  return render_template("trees.html",
                          title='Trees manager',
                          trees=user.allTrees(),
                          user=user)

@app.route('/mngtrees', methods = ['GET', 'POST'])
@login_required
def mngtrees():
  user = Users.getUser(email=g.user.email)

  if request.method == "GET":
    cmd = request.args.get('cmd', default='', type=str)

    if cmd == "create_tree":
      try:
        treename = request.args.get('name', default='NewTree', type=str)
        if user.getTree(name=treename) != None:
          raise BaseException
        createdTree = Tree(user, treename)
        return jsonify({ 'id' : createdTree.id, 'name' : createdTree.name })
      except BaseException:
        return jsonify({ 'error' : "Error: The tree with such name exists. Try another name.", })
    elif cmd == "remove_tree":
      try:
        tree_id = request.args.get('tree_id', default=None, type=int)
        tree = user.getTree(id=tree_id)
        tree.remove()
        return "True"
      except BaseException:
        return "False"
    elif cmd == "rename_tree":
      try:
        tree_id = request.args.get('tree_id', default=None, type=int)
        newname = request.args.get('newname', default='Tree', type=str)
        if user.getTree(name=newname) != None:
          raise BaseException
        tree = user.getTree(id=tree_id)
        tree.rename(newname)
        return ""
      except BaseException:
        return "Error: The tree with such name exists. Try another name."

  db.session.commit()
  return ""

@app.route('/mngtree', methods = ['GET', 'POST'])
def mngtree():
  #for_test()

  # get data from request
  ## via GET method
  if request.method == "GET":
    # curtree_id is require only for cases when jstree return '#' as a sign of root branch_id. To get rid of it we have to rewrite a big part of jstree
    try:
      curtree_id = request.args.get('tree_id', default='', type=str)
    except AttributeError as e:
      msg='Can\'t find any trees. Try to create one.'
      print('\n' + str(msg) + '\n')
      return ""

    import app.general
    nestedocs = app.general.str2bool(request.args.get('nestedocs', default='False', type=str))
    cmd = request.args.get('cmd', default='', type=str)
    id = request.args.get('id', default='', type=str)

    # after integration with flask symbole '%' has started to add to id. So we need to remove it
    if id[:1] == "%":
      id = int(id[1:])
    if id == '#' or id == None or id == '':
      curtree = Tree.getTree(id = curtree_id)
      id = curtree.rootb_id

    data = request.args.get('data', default='', type=str)

  ## via POST method
  else:
    form = SaveDataForm(request.form)
    if request.method == "POST" and form.validate():
      nestedocs = form.nestedocs.data
      cmd = form.cmd.data
      id = form.id.data
      data = form.data.data
  ##

  branch = Branch.get(id=id)
  curtree = Tree.getTree(id=branch.tree_id)
  tree_owner = curtree.owner

  """
  cmd = "load_subbs"
  id = 4
  id = '#'
  """

  # set permission for actions
  if g.user is not None and g.user.is_authenticated():
    curuser = g.user
  else:
    curuser = 'guest'

  owner = True
  if tree_owner.id != curuser.id:
    owner = False
    if not ( branch.read and cmd == "load_subbs" ):
      cmd = ''
  #

  if cmd != "" :
    if cmd == "fold":
      branch.folded = True
    elif cmd == "unfold":
      branch.folded = False
    elif cmd == "rename_node":
      branch.text = data
    elif cmd == "move_node":
      new_parent_id = request.args.get('new_parent', default=curtree.rootb_id, type=int)
      position = request.args.get('position', default=-1, type=int)
      branch.move(new_parent_id, position)
    elif cmd == "load_data":
      return branch.text
    elif cmd == "delete_node":
      branch.remove()
    elif cmd == "create_node":
      parent_id = request.args.get('parent_id', default=curtree.rootb_id, type=int)
      parentB = curtree.getB(parent_id)
      newB = Branch(main = (not nestedocs), parent_id = parent_id)
      position = request.args.get('position', default=-1, type=int)
      newB.move(pos=position)
      return str( newB.id )
    elif cmd == "load_subbs":
      curtree.set_latestB(id)
      return json.dumps(getList_subbsOf(branch, nestedocs, withReadLabel=(not owner)))
    elif cmd == "get_privileges":
      return json.dumps(branch.get_priv_all())
    elif cmd == "set_privileges":
      None
    else:
      if nestedocs :
        if cmd == "save_data":
          branch.text = data
        else:
          pass
  db.session.commit()
  return ""


"""
@app.route('/test')
def test():
  print("\ntest\n")
"""
