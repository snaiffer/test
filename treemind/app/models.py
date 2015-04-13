from app import db
from werkzeug.security import generate_password_hash, check_password_hash

"""
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
"""


"""
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
"""
import app.general

"""
Base = declarative_base()

db.engine = create_engine(
    str(app.general.dbtype) + "://" +
    str(app.general.dbuser_login) + ":" +
    str(app.general.dbuser_passwd) + "@" +
    str(app.general.dbaddr) + "/" +
    app.general.testdb)
Base.metadata.create_all(db.engine)
Session = sessionmaker(bind=db.engine)
db.session = Session()
"""

"""
Rules:
  ) If branch is subb of the root branch it has to have 'main=True' status
"""

class Forest(object):
  def remove(self):
    db.session.query(Tree).delete()
    db.session.query(Branch).delete()
    #db.db.engine.execute("ALTER SEQUENCE branches_id_seq RESTART;")
    db.engine.execute("ALTER SEQUENCE " + Tree.__tablename__ + "_id_seq RESTART;")
    db.engine.execute("ALTER SEQUENCE " + Branch.__tablename__ + "_id_seq RESTART;")
    db.session.commit()

  def allTrees(self):
    return db.session.query(Tree).all()

class Users(db.Model):
  __tablename__ = 'users'
  """
  id starts from 2. It is need for private settings.
    id with "0" means nobody has the privilage
    id with "1" means everybody has the privilage
  """
  id = db.Column(db.Integer, db.Sequence('users_id_seq', start=2, increment=1), primary_key=True)
  email = db.Column(db.String, index = True, unique = True)
  nickname = db.Column(db.String, index = True, unique = True)
  passwd = db.Column(db.String, index = True, unique = True)
  latestTree_id = db.Column(db.Integer)

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

  def __init__(self, nickname='', passwd='', email='', tree=None):
    self.nickname = nickname
    self.passwd = passwd
    self.email = email
    self.tree = tree
    self.latestTree_id = None

    db.session.add(self)
    db.session.commit()

  def getTree(self, id=None, name=None):
    if id != None:
      tree = db.session.query(Tree).filter_by(owner_id=self.id).filter_by(id=id).scalar()
    elif name != None:
      tree = db.session.query(Tree).filter_by(owner_id=self.id).filter_by(name=name).scalar()
    else:
      return None

    if tree != None:
      self.set_latestTree(tree.id)

    return tree

  def allTrees(self):
    return db.session.query(Tree).filter_by(owner_id=self.id).all()

  def remove(self):
    for curTree in self.allTrees():
      curTree.remove()
    db.session.delete(self)
    db.session.commit()

  def set_latestTree(self, id):
    self.latestTree_id = id
    db.session.commit()

  def get_latestTree(self):
    """ get the tree which has been used at the lastest time """
    if self.latestTree_id == None:
      allT = self.allTrees()
      if ( len(allT) != 0 ):
        return allT[0]
      else:
        return None
    return self.getTree(id = self.latestTree_id)

  def removeAll(self):
    db.session.query(Users).delete()
    #db.db.engine.execute("ALTER SEQUENCE branches_id_seq RESTART;")
    db.engine.execute("ALTER SEQUENCE " + Users.__tablename__ + "_id_seq RESTART;")
    db.session.commit()

  def getUser(self=None, email=None, nickname=None):
    if email != None:
      return db.session.query(Users).filter_by(email=email).scalar()
    if nickname != None:
      return db.session.query(Users).filter_by(nickname=nickname).scalar()
    return None

class Tree(db.Model):
  __tablename__ = 'trees'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  rootb_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
  rootb = db.relationship("Branch", single_parent=True, cascade='all, delete-orphan', backref='tree')
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  owner = db.relationship("Users", backref='trees')
  latestB_id = db.Column(db.Integer)

  def __init__(self, owner=None, name='', rootb=None):
    self.name = name
    self.owner = owner
    self.latestB_id = None

    db.session.add(self)
    db.session.commit()

    if rootb == None:
      rootb = self.init()
    self.rootb = rootb

    owner = Users.query.filter_by(id = owner.id).first()
    owner.set_latestTree(self.id)
    db.session.commit()

  def init(self):
    rootbg = db.session.query(Branch).filter_by(id=app.general.rootBglobal_id).scalar()
    if (rootbg == None):
      rootbg = Branch(id=app.general.rootBglobal_id)
    rootb = Branch(text = "root_" + self.name, folded=False, main = True, parent = rootbg, tree_id = self.id)
    firstb = Branch(text = "first branch", folded=False, main = True, parent = rootb)
    return rootb

  def set_latestB(self, id):
    while self.getB(id).main == False:
      id = self.getB(id).parent_id
    if id != self.rootb_id:
      self.latestB_id = id
      db.session.commit()

  def get_latestB(self):
    """ get the branch which has been used at the lastest time """
    if self.latestB_id == None:
      return self.rootb
    return self.getB(self.latestB_id)

  def remove(self):
    rootb = self.getB_root()
    rootb.remove()
    db.session.delete(self)
    db.session.commit()

  def rename(self, newname):
    self.name = newname
    db.session.commit()

  def moveB(self, branch, parent_id = None, pos = -1):
    branch.move(parent_id, pos)

  def getB(self, id):
    return db.session.query(Branch).filter_by(id=id).scalar()

  def getB_root(self):
    return self.rootb

  def getTree(id=None):
    if id == None:
      return None
    return db.session.query(Tree).filter_by(id=id).scalar()

class Branch(db.Model):
  __tablename__ = 'branches'
  id = db.Column(db.Integer, db.Sequence('branches_id_seq', start=app.general.rootBglobal_id, increment=1), primary_key=True)
  main = db.Column(db.Boolean, default='False')
  folded = db.Column(db.Boolean, default='False')
  orderb = db.Column(db.Integer, index=True, default=0)
  parent_id = db.Column(db.Integer, db.ForeignKey(id))
  subbs = db.relationship('Branch',
    # cascade deletions
    cascade="all, delete-orphan",

    # many to one + adjacency list - remote_side is required to reference the 'remote'
    # column in the join condition.
    backref=db.backref("parent", remote_side=id),
    )
  text = db.Column(db.String, default='')
  tree_id = db.Column(db.Integer)
  read = db.Column(db.Boolean, default='False') # Allowed read for other users

  def __init__(self, id=None, text=None, main=False, folded=False, parent=None, parent_id=None, tree_id = None, read=False):
    if id == app.general.rootBglobal_id :
      self.text = "root_global"
      self.folded = False
      self.main = True
      self.tree_id = 0
      self.parent_id = None
    else:
      self.text = text
      if parent == None and parent_id == None:
        parent_id = app.general.rootBglobal_id
      self.folded = folded
      self.parent = parent
      self.parent_id = parent_id
      self.set_main(main)

      self.read = read

      db.session.add(self)
      db.session.commit()

      if tree_id == None:
        if self.parent == None:
          parent = db.session.query(Branch).filter_by(id=parent_id).scalar()
        tree_id = parent.tree_id
      self.tree_id = tree_id

      self.move(pos = -1)

      """
      # for rootb_global case
      if self.id == parent_id :
        self.parent_id = None
        db.session.commit()
      """
    db.session.add(self)
    db.session.commit()

  def get_subbs(self):
    """
    Return subbs of the branch in sorted order.
    Use it instead of branch.subbs!!!
      branch.subbs:
        - return unodered list
        - know nothing about 'tree'
    """
    subbs = db.session.query(Branch).filter_by(parent_id=self.id).order_by('orderb').all()
    return subbs

  def get_subbsCount(self):
    return db.session.query(Branch).filter_by(parent_id=self.id).count()

  def remove(self):
    db.session.delete(self)
    db.session.commit()

  def _reindexing_orderb(self, parent_id):
    """ Reindex orderb column for branches under parent_id """
    listB = db.session.query(Branch).filter_by(parent_id = parent_id).order_by('orderb').all()
    cur_orderb = 0
    for curB in listB:
      cur_orderb += app.general.orderb_step
      if cur_orderb >= app.general.orderb_MAX :
        raise NumOforedersIsExpired
      curB.orderb = cur_orderb

  def move(self, parent_id = None, pos = -1):
    """
    Move branch to the position of branch under parent_id with id = parent_id
    parent_id == None   --parent of the branch won't be changed
    pos >= 0
    pos == -1  --move branch to the end
    in other case will be raised "NegativePosition" exception
    """
    self._move(parent_id, pos)
    db.session.commit()

  def _move(self, parent_id, pos):
    branch = self
    _parent_id = branch.parent_id
    # find out if the position of moving is the same. If it is so then do nothing
    if ( (parent_id == None or parent_id == _parent_id) and pos != -1 ):
      curpos = branch.parent.get_subbs().index(branch)
      if ( curpos == pos ):
        return
    if ( parent_id != None ):
      _parent_id = parent_id

    if pos == -1:
      lowestb = db.session.query(Branch).filter_by(parent_id = _parent_id).order_by(db.desc('orderb')).first()
      if ( lowestb == None ):
        branch.orderb = app.general.orderb_step   # start numeration from begining
      else:
        if lowestb.orderb >= app.general.orderb_MAX :
          self._reindexing_orderb(_parent_id)
          branch.move(_parent_id, pos)
          return
        branch.orderb = lowestb.orderb + app.general.orderb_step
    elif pos >= 0:
      leftNeigh = 0
      if pos > 0:
        leftNeighB = db.session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos-1).limit(1).first()
        leftNeigh = leftNeighB.orderb
        # if the branch is moved down we have to increment pos (to ommit the branch)
        if leftNeigh >= branch.orderb :
          pos += 1
          leftNeighB = db.session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos-1).limit(1).first()
          leftNeigh = leftNeighB.orderb
      rightNeighB = db.session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos).limit(1).first()
      rightNeigh = rightNeighB.orderb
      addit = (rightNeigh - leftNeigh) / 2
      if int(addit) <= 1:
        self._reindexing_orderb(_parent_id)
        branch.move(_parent_id, pos)
        return
      branch.orderb = int(leftNeigh + addit)
    else:
      raise NegativePosition(connection=db.session)

    if _parent_id :
      par = branch.parent
      branch.parent_id = _parent_id
      self.set_main(self.main)

  def set_main(self, main = True):
    """
    set main with according the rule:
      ) If branch is subb of the root branch it has to have 'main=True' status
    """
    if main == False:
      if (self.parent and self.parent.tree) or db.session.query(Tree).filter_by(rootb_id = self.parent_id).count() != 0:
        main = True
    self.main = main
    db.session.commit()

  def get(self=None, id=None):
    if id == None:
      return None
    return db.session.query(Branch).filter_by(id=id).scalar()

  def __repr__(self):
    return self.text

  def __str__(self):
    return self.text

class BranchException(Exception):
  def __init__(self, connection=None):
    if hasattr(connection, 'rollback') and connection != None:
      connection.rollback()
  def _output(self, msg):
    print("Tree: " + str(msg))

class NegativePosition(BranchException):
  def __init__(self, connection=None):
    BranchException.__init__(self, connection)
    self._output("Error: the position of the branch can't be negative!")

class NumOforedersIsExpired(BranchException):
  def __init__(self, connection=None):
    BranchException.__init__(self, connection)
    self._output("Error: numbers of orderb is expired!\n  Note: you can decrease app.general.orderb_step to solve this problem")


"""
def test(forestName = app.general.testdb):
  import sys

  #self.db.session = Session()
  Base.metadata.create_all(db.engine)
  Session = sessionmaker(bind=db.engine)
  db.session = Session()

  Forest().remove()
  Users().removeAll()

  print("Test:")
  try:
    alex = Users("Alex", "123", "alex@gmail.com")
    bob = Users("Bob", "123456", "bob@gmail.com")

    testTree1 = Tree(alex, "testTree1")
    testTree2 = Tree(alex, "testTree2")
    testTree3 = Tree(bob, "testTree3")
    testTree4 = Tree(alex, "testTree4")

    sys.stdout.write("  ) Get the lastest used tree (before using):\t")
    if ( alex.get_latestTree() == None ):
      raise BaseException("A tree wasn't got")
    print('OK')

    sys.stdout.write("  ) Test for separation trees by users:\t")
    if ( len(alex.allTrees()) != 3):
      raise BaseException("Separation trees by users has faild")
    print('OK')

    sys.stdout.write("  ) Get tree for user:\t")
    if ( alex.getTree(id = testTree2.id) == None ):
      raise BaseException("The tree hasn't been got")
    print('OK')

    sys.stdout.write("  ) Tree protection from accessiong by another user (not owner):\t")
    if ( alex.getTree(id = testTree3.id) != None):
      raise BaseException("Tree protection has faild")
    print('OK')

    sys.stdout.write("  ) Get the lastest used tree (after using):\t")
    if ( alex.get_latestTree() == None ):
      raise BaseException("A tree wasn't got")
    print('OK')

    curtree = testTree2
    rootb = curtree.getB_root()

    print("  ) Creating branches:  ")
    sys.stdout.write("    )) If branch is subb of the root branch it has to have 'main=True' status:\t")
    b1 = Branch(text="branch1", main=False, parent=rootb)
    if ( not b1.main ):
      raise BaseException("The branch is subbs of the root branch but hasn't 'main=True' status")
    print('OK')
    sys.stdout.write("    )) Creating ordinary branches and subbs:\t")
    b2 = Branch(text="branch2", main=True, parent=rootb)
    b3 = Branch(text="branch3", main=True, parent=rootb)
    b11 = Branch(text="branch11", parent=b1)
    b12 = Branch(text="branch12", parent=b1)
    print('OK')

    sys.stdout.write("  ) Order of branches tests:\t")
    if b11.orderb != (1 * app.general.orderb_step):
      raise BaseException("Moving problem")
    if b12.orderb != (2 * app.general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    print("  ) Branches moving:  ")
    sys.stdout.write("    )) General moving test:\t")
    b21 = Branch(text="branch21", main=True, parent=curtree.rootb)
    b2.move(b21.id)

    b22 = Branch(text="branch22")
    b23 = Branch(text="branch23")
    b22.move(parent_id = b2.id)
    b23.move(parent_id = b2.id)
    if b2.get_subbsCount() != 2:
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("    )) Moving to the begin:\t")
    b23.move(pos = 0)
    if b23.orderb != (0.5 * app.general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("    )) Moving to the end:\t")
    b23.move()
    if b23.orderb != (2 * app.general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("    )) Moving the latest subb to the rootb:\t")
    b23.move(rootb.id)
    if not b23.main :
      raise BaseException("The branch is subbs of the root branch but hasn't 'main=True' status")
    print('OK')

    b31 = Branch(text="branch31", parent=b3)
    b32 = Branch(text="branch32", parent=b3)
    b33 = Branch(text="branch33", parent=b3)

    sys.stdout.write("    )) Moving to the same position:\t")
    b31.move(pos = 0)
    if b31.orderb != (1 * app.general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("    )) Moving to the position between two existent branches:\t")
    b31.move(pos = 1)
    if b31.orderb != (2.5 * app.general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("  ) Getting tests:\t")
    # get branch
    rootb = curtree.getB_root()
    rootb = curtree.rootb
    bget = curtree.getB(rootb.id)

    # get fields
    b1.id
    b1.text
    b1.main
    b1.folded
    b1.parent
    b1.get_subbs()
    b12 = curtree.getB(b1.get_subbs()[0].id)
    for curB in b1.get_subbs():
      curB.text
    b1.get_subbsCount()
    print('OK')

    sys.stdout.write("  ) Changing text field:\t")
    b1.text = "TEST"
    print('OK')

    print("  ) Reindexing orderb field:\t")
    b5 = Branch(text="branch5", parent=rootb)
    b51 = Branch(text="branch51", parent=b5)
    b52 = Branch(text="branch52", parent=b5)

    sys.stdout.write("    )) If orderb is higher than MAX value :\t")
    b52.orderb = app.general.orderb_MAX
    b51.move()
    if b51.orderb != (3 * app.general.orderb_step) :
      raise BaseException("Reindexing problem")
    print('OK')

    sys.stdout.write("    )) If orderb is lower than MIN value :\t")
    b52.orderb = b5.get_subbs()[0].orderb - app.general.orderb_step
    b51.move(pos = 0)
    if b51.orderb != (0.5 * app.general.orderb_step) :
      raise BaseException("Reindexing problem")
    print('OK')

    print("  ) Get the latest used branch:\t")
    sys.stdout.write("    )) Before set:\t")
    if ( curtree.get_latestB().id != curtree.rootb_id ):
      raise BaseException("The latest used branch hasn't benn got")
    print('OK')

    curtree.set_latestB(b5.id)
    sys.stdout.write("    )) After set:\t")
    if ( curtree.get_latestB().id != b5.id ):
      raise BaseException("The latest used branch hasn't benn got")
    print('OK')

    print("  ) Removing branches:\t")
    sys.stdout.write("    )) Simple removing:\t")
    idB = b1.id
    b1.remove()
    if curtree.getB(b1.id) != None:
      raise BaseException("The branch hasn't been removed!")
    print('OK')

    sys.stdout.write("    )) Removing all branches from the tree:\t")
    for curB in rootb.get_subbs():
      curB.remove()
    if ( rootb.get_subbsCount() != 0 ):
      raise BaseException("All branches haven't been removed!")
    print('OK')

    sys.stdout.write("  ) Removing all branches of the tree which is removing:\t")
    curtree.remove()
    if ( db.session.query(Branch).filter_by(id=rootb.id).scalar() != None ):
      raise BaseException("The branches of the tree haven't been removed!")
    print('OK')

    sys.stdout.write("  ) Removing user with his trees:\t")
    alex.remove()
    if ( db.session.query(Tree).filter_by(id=testTree4.id).scalar() != None ):
      raise BaseException("The trees haven't been removed!")
    print('OK')

  except BaseException as e:
    print(e)
    print("\nSummary:\tFAILD")
  else:
    print("\nSummary:\tOK")

if __name__ == '__main__':
  test()
"""
