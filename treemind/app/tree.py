#!/usr/bin/env python3.2

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
import general

Base = declarative_base()

engine = create_engine(
    str(general.dbtype) + "://" +
    str(general.dbuser_login) + ":" +
    str(general.dbuser_passwd) + "@" +
    str(general.dbaddr) + "/" +
    general.testdb)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

"""
Rules:
  ) If branch is subb of the root branch it has to have 'main=True' status
"""

class Forest(object):
  def remove(self):
    session.query(Tree).delete()
    session.query(Branch).delete()
    #db.engine.execute("ALTER SEQUENCE branches_id_seq RESTART;")
    engine.execute("ALTER SEQUENCE " + Tree.__tablename__ + "_id_seq RESTART;")
    engine.execute("ALTER SEQUENCE " + Branch.__tablename__ + "_id_seq RESTART;")
    session.commit()

  def allTrees(self):
    return session.query(Tree).all()


class Users(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  email = Column(String, unique = True)
  nickname = Column(String)
  passwd = Column(String)
  latestTree_id = Column(Integer)

  def __init__(self, email='', nickname='', passwd='', tree=None):
    self.email = email
    self.nickname = nickname
    self.passwd = passwd
    self.tree = tree
    self.latestTree_id = None

    session.add(self)
    session.commit()

  def getTree(self, treeID):
    tree = session.query(Tree).filter_by(owner_id=self.id).filter_by(id=treeID).scalar()
    if tree != None :
      self.latestTree_id = treeID
      session.commit()
    return tree

  def allTrees(self):
    return session.query(Tree).filter_by(owner_id=self.id).all()

  def remove(self):
    for curTree in self.allTrees():
      curTree.remove()
    session.delete(self)
    session.commit()

  def get_latestTree(self):
    """ get the tree which has been used at the lastest time """
    if self.latestTree_id == None:
      allT = self.allTrees()
      if ( len(allT) != 0 ):
        return allT[0]
    return self.getTree(self.latestTree_id)

  def removeAll(self):
    session.query(Users).delete()
    #db.engine.execute("ALTER SEQUENCE branches_id_seq RESTART;")
    engine.execute("ALTER SEQUENCE " + Users.__tablename__ + "_id_seq RESTART;")
    session.commit()

class Tree(Base):
  __tablename__ = 'trees'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  rootb_id = Column(Integer, ForeignKey('branches.id'))
  rootb = relationship("Branch", single_parent=True, cascade='all, delete-orphan', backref='tree')
  owner_id = Column(Integer, ForeignKey('users.id'))
  owner = relationship("Users", backref='trees')
  latestB_id = Column(Integer)

  def __init__(self, owner=None, name='', rootb=None):
    self.name = name
    if rootb == None:
      rootb = self.init()
    self.rootb = rootb
    self.owner = owner
    self.latestB_id = None

    session.add(self)
    session.commit()

  def init(self):
    rootbg = session.query(Branch).filter_by(id=general.rootBglobal_id).scalar()
    if (rootbg == None):
      rootbg = Branch(text = "root_global", folded=False, main = True)
    rootb = Branch(text = "root_" + self.name, folded=False, main = True, parent = rootbg)
    return rootb

  def set_latestB(self, id):
    self.latestB_id = id
    session.commit()

  def get_latestB(self):
    """ get the branch which has been used at the lastest time """
    if self.latestB_id == None:
      return self.rootb
    return self.getB(self.latestB_id)

  def remove(self):
    session.delete(self)
    session.commit()

  def moveB(self, branch, parent_id = None, pos = -1):
    branch.move(parent_id, pos)

  def getB(self, id):
    return session.query(Branch).filter_by(id=id).scalar()

  def getB_root(self):
    return self.rootb

class Branch(Base):
  __tablename__ = 'branches'
  id = Column(Integer, primary_key=True)
  main = Column(Boolean, default='False')
  folded = Column(Boolean, default='False')
  orderb = Column(Integer, index=True, default=0)
  parent_id = Column(Integer, ForeignKey(id))
  subbs = relationship('Branch',
    # cascade deletions
    cascade="all, delete-orphan",

    # many to one + adjacency list - remote_side is required to reference the 'remote'
    # column in the join condition.
    backref=backref("parent", remote_side=id),
    )
  text = Column(String, default='')

  def __init__(self, text=None, main=False, folded=False, parent=None, parent_id=None):
    self.text = text
    if parent == None and parent_id == None:
      parent_id = general.rootBglobal_id
    self.folded = folded
    self.parent = parent
    self.parent_id = parent_id
    self.set_main(main)

    session.add(self)
    session.commit()

    if ( self.id != general.rootBglobal_id ):
      self.move(pos = -1)

    # for rootb_global case
    if self.id == parent_id :
      self.parent_id = None
      session.commit()

  def get_subbs(self):
    """
    Return subbs of the branch in sorted order.
    Use it instead of branch.subbs!!!
      branch.subbs:
        - return unodered list
        - know nothing about 'tree'
    """
    subbs = session.query(Branch).filter_by(parent_id=self.id).order_by('orderb').all()
    return subbs

  def get_subbsCount(self):
    return session.query(Branch).filter_by(parent_id=self.id).count()

  def remove(self):
    session.delete(self)
    session.commit()

  def _reindexing_orderb(self, parent_id):
    """ Reindex orderb column for branches under parent_id """
    listB = session.query(Branch).filter_by(parent_id = parent_id).order_by('orderb').all()
    cur_orderb = 0
    for curB in listB:
      cur_orderb += general.orderb_step
      if cur_orderb >= general.orderb_MAX :
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
    session.commit()

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
      lowestb = session.query(Branch).filter_by(parent_id = _parent_id).order_by(desc('orderb')).first()
      if ( lowestb == None ):
        branch.orderb = general.orderb_step   # start numeration from begining
      else:
        if lowestb.orderb >= general.orderb_MAX :
          self._reindexing_orderb(_parent_id)
          branch.move(_parent_id, pos)
          return
        branch.orderb = lowestb.orderb + general.orderb_step
    elif pos >= 0:
      leftNeigh = 0
      if pos > 0:
        leftNeighB = session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos-1).limit(1).first()
        leftNeigh = leftNeighB.orderb
        # if the branch is moved down we have to increment pos (to ommit the branch)
        if leftNeigh >= branch.orderb :
          pos += 1
          leftNeighB = session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos-1).limit(1).first()
          leftNeigh = leftNeighB.orderb
      rightNeighB = session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos).limit(1).first()
      rightNeigh = rightNeighB.orderb
      addit = (rightNeigh - leftNeigh) / 2
      if int(addit) <= 1:
        self._reindexing_orderb(_parent_id)
        branch.move(_parent_id, pos)
        return
      branch.orderb = int(leftNeigh + addit)
    else:
      raise NegativePosition(connection=session)

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
      if (self.parent and self.parent.tree) or session.query(Tree).filter_by(rootb_id = self.parent_id).count() != 0:
        main = True
    self.main = main
    session.commit()

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
    self._output("Error: numbers of orderb is expired!\n  Note: you can decrease general.orderb_step to solve this problem")


def test(forestName = general.testdb):
  import sys

  #self.session = Session()
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()

  Forest().remove()
  Users().removeAll()

  print("Test:")
  try:
    alex = Users("Alex", "123", "alex@gmail.com")
    bob = Users("Bob", "123456", "bob@gmail.com")
    """
    sys.stdout.write("  ) Test for creating the same user:\t")
    try:
      alex2 = Users("Alex", "123", "alex@gmail.com")
    except BaseException:
      print('OK')
      session.rollback()
    else:
      raise BaseException("The same user has been created!")
    """

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
    if ( alex.getTree(testTree2.id) == None ):
      raise BaseException("The tree hasn't been got")
    print('OK')

    sys.stdout.write("  ) Tree protection from accessiong by another user (not owner):\t")
    if ( alex.getTree(testTree3.id) != None):
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
    if b11.orderb != (1 * general.orderb_step):
      raise BaseException("Moving problem")
    if b12.orderb != (2 * general.orderb_step):
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
    if b23.orderb != (0.5 * general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("    )) Moving to the end:\t")
    b23.move()
    if b23.orderb != (2 * general.orderb_step):
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
    if b31.orderb != (1 * general.orderb_step):
      raise BaseException("Moving problem")
    print('OK')

    sys.stdout.write("    )) Moving to the position between two existent branches:\t")
    b31.move(pos = 1)
    if b31.orderb != (2.5 * general.orderb_step):
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
    b52.orderb = general.orderb_MAX
    b51.move()
    if b51.orderb != (3 * general.orderb_step) :
      raise BaseException("Reindexing problem")
    print('OK')

    sys.stdout.write("    )) If orderb is lower than MIN value :\t")
    b52.orderb = b5.get_subbs()[0].orderb - general.orderb_step
    b51.move(pos = 0)
    if b51.orderb != (0.5 * general.orderb_step) :
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
    if ( session.query(Branch).filter_by(id=rootb.id).scalar() != None ):
      raise BaseException("The branches of the tree haven't been removed!")
    print('OK')

    sys.stdout.write("  ) Removing user with his trees:\t")
    alex.remove()
    if ( session.query(Tree).filter_by(id=testTree4.id).scalar() != None ):
      raise BaseException("The trees haven't been removed!")
    print('OK')

  except BaseException as e:
    print(e)
    print("\nSummary:\tFAILD")
  else:
    print("\nSummary:\tOK")

if __name__ == '__main__':
  test()
