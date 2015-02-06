#!/usr/bin/env python3.2

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
import general

Base = declarative_base()

"""
Rules:
  ) Root branch has to contain at least one main branch
  ) Any main branch has to contain at least one notMain branch
  ) If branch is subb of the root branch it has to have 'main=True' status
"""

class Tree():
  def __init__(self, name, session = None):
    self.name = name
    self.session = session

  def __enter__(self, *args):
    if self.session:
      return self.session
    engine = create_engine(
        str(general.dbtype) + "://" +
        str(general.dbuser_login) + ":" +
        str(general.dbuser_passwd) + "@" +
        str(general.dbaddr) + "/" +
        self.name)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    self.session = Session()
    return self

  def __exit__(self, *args):
    self.session.commit()
    self.session.close()

  def init(self):
    rootb = Branch(tree=self, text = "root", folded=False, main = True, parent_id = None)
    firstb = Branch(tree=self, text = "", folded=False, main = True, parent_id = rootb.id)

  def reindexing_orderb(self, parent_id):
    """ Reindex orderb column for branches under parent_id """
    listB = self.session.query(Branch).filter_by(parent_id = parent_id).order_by('orderb').all()
    cur_orderb = 0
    for curB in listB:
      cur_orderb += general.orderb_step
      if cur_orderb >= general.orderb_MAX :
        raise NumOforedersIsExpired
      curB.orderb = cur_orderb

  def moveB(self, branch, parent_id = None, pos = -1):
    """
    Move branch to the position of branch under parent_id with id = parent_id
    parent_id == None   --parent of the branch won't be changed
    pos >= 0
    pos == -1  --move branch to the end
    in other case will be raised "NegativePosition" exception
    """
    _parent_id = branch.parent_id
    # find out if the position of moving is the same. If it is so then do nothing
    if ( (parent_id == None or parent_id == _parent_id) and pos != -1 ):
      curpos = self.getSubBs(branch.parent).index(branch)
      if ( curpos == pos ):
        return
    if ( parent_id != None ):
      _parent_id = parent_id

    if pos == -1:
      lowestb = self.session.query(Branch).filter_by(parent_id = _parent_id).order_by(desc('orderb')).first()
      if ( lowestb == None ):
        branch.orderb = general.orderb_step   # start numeration from begining
      else:
        if lowestb.orderb >= general.orderb_MAX :
          self.reindexing_orderb(_parent_id)
          self.moveB(branch, _parent_id, pos)
          return
        branch.orderb = lowestb.orderb + general.orderb_step
    elif pos >= 0:
      leftNeigh = 0
      if pos > 0:
        leftNeighB = self.session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos-1).limit(1).first()
        leftNeigh = leftNeighB.orderb
        # if the branch is moved down we have to increment pos (to ommit the branch)
        if leftNeigh >= branch.orderb :
          pos += 1
          leftNeighB = self.session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos-1).limit(1).first()
          leftNeigh = leftNeighB.orderb
      rightNeighB = self.session.query(Branch).filter_by(parent_id = _parent_id).order_by('orderb').offset(pos).limit(1).first()
      rightNeigh = rightNeighB.orderb
      addit = (rightNeigh - leftNeigh) / 2
      if int(addit) <= 1:
        self.reindexing_orderb(_parent_id)
        self.moveB(branch, _parent_id, pos)
        return
      branch.orderb = int(leftNeigh + addit)
    else:
      raise NegativePosition(connection=self.session)

    if _parent_id :
      par = branch.parent
      branch.parent_id = _parent_id
      self._check_forContainNotMainB(par)
      self._check_forRightMainStatus(branch)
    self.session.commit()

  def _add(self, branch):
    self.session.add(branch)
    self.session.commit()
    if ( branch.id != general.rootB_id ):
      self.moveB(branch, pos = -1)

  def _add_all(self, *branches):
    for curb in branches:
      self._add(curb)

  def _check_forContainNotMainB(self, branch):
    """ Any main branch has to contain one notMain branch at least """
    if ( branch.main == True and branch.get_subbsCount() == 0):
      subb = Branch(tree=self, text = "", folded=False, main = False, parent_id = branch.id)

  def _check_forRootSubb(self):
    """ root branch has to contain at least one main branch """
    rootb = self.getB_root()
    if ( rootb.get_subbsCount() == 0 ):
      firstb = Branch(tree=self, text = "", folded=False, main = True, parent_id = rootb.id)

  def _check_forRightMainStatus(self, branch):
    if ( branch.parent_id == general.rootB_id ):
      if ( branch.main == False ):
        branch.main = True

  def _check_all(self, branch):
    self._check_forRootSubb()
    self._check_forContainNotMainB(branch)
    self._check_forRightMainStatus(branch)

  def remove(self, branch):
    self.session.delete(branch)
    self._check_forRootSubb()
    self._check_forContainNotMainB(branch.parent)

  def getB(self, id):
    resB = self.session.query(Branch).filter_by(id=id).scalar()
    resB.tree = self
    return resB

  def getB_root(self):
    return self.getB(general.rootB_id)

  def getSubBs(self, branch):
    """ Return subbs of the branch in sorted order """
    subbs = self.session.query(Branch).filter_by(parent_id=branch.id).order_by('orderb').all()
    for curb in subbs:
      curb.tree = self
    return subbs

  def getSubBsCount(self, branch):
    return self.session.query(Branch).filter_by(parent_id=branch.id).count()

class TreeException(Exception):
  def __init__(self, connection=None):
    if hasattr(connection, 'rollback') and connection != None:
      connection.rollback()
  def _output(self, msg):
    print("Tree: " + str(msg))

class NegativePosition(TreeException):
  def __init__(self, connection=None):
    TreeException.__init__(self, connection)
    self._output("Error: the position of the branch can't be negative!")

class NumOforedersIsExpired(TreeException):
  def __init__(self, connection=None):
    TreeException.__init__(self, connection)
    self._output("Error: numbers of orderb is expired!\n  Note: you can decrease general.orderb_step to solve this problem")

class Branch(Base):
  __tablename__ = 'branches'
  id = Column(Integer, primary_key=True)
  main = Column(Boolean, default='False')
  folded = Column(Boolean, default='False')
  parent_id = Column(Integer, ForeignKey(id))
  orderb = Column(Integer, index=True, default=0)
  text = Column(String, default='')
  subbs = relationship('Branch',
    # cascade deletions
    cascade="all, delete-orphan",

    # many to one + adjacency list - remote_side
    # is required to reference the 'remote' 
    # column in the join condition.
    backref=backref("parent", remote_side=id),
    )

  def __init__(self, tree, text='', main=False, folded=False, parent=None, parent_id=general.rootB_id):
    self.tree = tree
    self.text = text
    self.main = main
    self.folded = folded
    self.parent = parent
    self.parent_id = parent_id
    self.tree._add(self)
    tree._check_forRightMainStatus(self)
    tree._check_forContainNotMainB(self)

  def get_subbs(self):
    """
    Return subbs of the branch in sorted order.
    Use it instead of branch.subbs!!!
      branch.subbs:
        - return unodered list
        - know nothing about 'tree'
    """
    return self.tree.getSubBs(self)

  def get_subbsCount(self):
    return self.tree.getSubBsCount(self)

  def move(self, parent_id = None, pos = -1):
    self.tree.moveB(self, parent_id, pos)

  def __repr__(self):
    return self.text

  def __str__(self):
    return self.text


def test(tree = general.testdb):
  import sys

  # cleaning
  import forest
  try:
    with forest.Forest() as f:
      f.removeTree(tree)
      f.plantTree(tree)
  except forest.ForestException:
    print("Error: ForestException has occured")

  print("Test:")
  try:
    with Tree(tree) as curtree:
      rootb = curtree.getB_root()

      print("  ) Creating branches:  ")
      sys.stdout.write("    )) If branch is subb of the root branch it has to have 'main=True' status:\t")
      b1 = Branch(tree=curtree, text="branch1", main=False, parent=rootb)
      if ( not b1.main ):
        raise BaseException("The branch is subbs of the root branch but hasn't 'main=True' status")
      print('OK')
      sys.stdout.write("    )) Creating ordinary branches and subbs:\t")
      b2 = Branch(tree=curtree, text="branch2", main=True, parent=rootb)
      b3 = Branch(tree=curtree, text="branch3", main=True, parent=rootb)
      b11 = Branch(tree=curtree, text="branch11", parent=b1)
      b12 = Branch(tree=curtree, text="branch12", parent=b1)
      print('OK')

      sys.stdout.write("  ) Order of branches tests:\t")
      if b11.orderb != (2 * general.orderb_step):
        raise BaseException("Moving problem")
      if b12.orderb != (3 * general.orderb_step):
        raise BaseException("Moving problem")
      print('OK')

      print("  ) Branches moving:  ")
      sys.stdout.write("    )) General moving test:\t")
      b21 = Branch(tree=curtree, text="branch21", main=True)
      b2.move(b21.id)

      b22 = Branch(tree=curtree, text="branch22")
      b23 = Branch(tree=curtree, text="branch23")
      curtree.moveB(b22, parent_id = b2.id)
      b23.move(parent_id = b2.id)
      if b2.get_subbsCount() != 3:
        raise BaseException("Moving problem")
      print('OK')

      sys.stdout.write("    )) Moving to the begin:\t")
      b23.move(pos = 0)
      if b23.orderb != (0.5 * general.orderb_step):
        raise BaseException("Moving problem")
      print('OK')

      sys.stdout.write("    )) Moving to the end:\t")
      b23.move()
      if b23.orderb != (3 * general.orderb_step):
        raise BaseException("Moving problem")
      print('OK')

      sys.stdout.write("    )) Moving the latest subb to the rootb:\t")
      b231 = b23.get_subbs()[0]
      b231.move(rootb.id)
      if b23.get_subbsCount() == 0 :
        raise BaseException("Empty branch hasn't been created")
      if not b231.main :
        raise BaseException("The branch is subbs of the root branch but hasn't 'main=True' status")
      print('OK')

      b31 = Branch(tree=curtree, text="branch31", parent=b3)
      b32 = Branch(tree=curtree, text="branch32", parent=b3)
      b33 = Branch(tree=curtree, text="branch33", parent=b3)

      sys.stdout.write("    )) Moving to the same position:\t")
      curtree.moveB(b31, pos = 1)
      if b31.orderb != (2 * general.orderb_step):
        raise BaseException("Moving problem")
      print('OK')

      sys.stdout.write("    )) Moving to the position between two existent branches:\t")
      curtree.moveB(b31, pos = 2)
      if b31.orderb != (3.5 * general.orderb_step):
        raise BaseException("Moving problem")
      print('OK')

      sys.stdout.write("  ) Getting tests:\t")
      # get branch
      rootb = curtree.getB_root()
      b1 = curtree.getB(8)

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
      b5 = Branch(tree=curtree, text="branch5", parent=rootb)
      b51 = Branch(tree=curtree, text="branch51", parent=b5)
      b52 = Branch(tree=curtree, text="branch52", parent=b5)

      sys.stdout.write("    )) If orderb is higher than MAX value :\t")
      b52.orderb = general.orderb_MAX
      curtree.moveB(b51)
      if b51.orderb != (4 * general.orderb_step) :
        raise BaseException("Reindexing problem")
      print('OK')

      sys.stdout.write("    )) If orderb is lower than MIN value :\t")
      b52.orderb = b5.get_subbs()[0].orderb - general.orderb_step
      curtree.moveB(b51, pos = 0)
      if b51.orderb != (0.5 * general.orderb_step) :
        raise BaseException("Reindexing problem")
      print('OK')

      print("  ) Removing branches:\t")
      sys.stdout.write("    )) Simple removing:\t")
      curtree.remove(b1)
      try:
        curtree.getB(8)
      except BaseException:
        print('OK')

      sys.stdout.write("    )) Removing the latest notMain branch:\t")
      b4 = Branch(tree=curtree, text="branch4", main=True, parent=rootb)
      b41 = Branch(tree=curtree, text="branch41", main=False, parent=b4)
      curtree.remove(b41)
      if ( b4.get_subbsCount() == 0 ):
        raise BaseException("The main branch remains without any notMain branches")
      print('OK')

      sys.stdout.write("    )) Removing all branches from the tree:\t")
      for curB in rootb.get_subbs():
        curtree.remove(curB)
      if ( rootb.get_subbsCount() != 1 ):
        raise BaseException("All branches have been removed!")
      print('OK')

  except BaseException as e:
    print(e)
    print("\nSummary:\tFAILD")
  else:
    print("\nSummary:\tOK")

if __name__ == '__main__':
  test()
