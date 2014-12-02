#!/usr/bin/env python3.2

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
import general

Base = declarative_base()

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
    rootb = Branch(tree=self, caption = "root", text = "root", main = True, parent_id = None)

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
    parent_id == None   --parent of the branche won't be changed
    pos >= 0
    pos == -1  --move branch to the end
    in other case will be raised "NegativePosition" exception
    """
    if parent_id :
      branch.parent_id = parent_id
      self.session.commit()

    if pos == -1:
      lowestb = self.session.query(Branch).filter_by(parent_id = branch.parent_id).order_by(desc('orderb')).first()
      if lowestb.orderb >= general.orderb_MAX :
        self.reindexing_orderb(branch.parent_id)
        self.moveB(branch, parent_id, pos)
        return
      branch.orderb = lowestb.orderb + general.orderb_step
    elif pos >= 0:
      leftNeigh = 0
      if pos > 0:
        leftNeighB = self.session.query(Branch).filter_by(parent_id = branch.parent_id).order_by('orderb').offset(pos-1).limit(1).first()
        leftNeigh = leftNeighB.orderb
        # if the branch is moved down we have to increment pos (to ommit the branch)
        if leftNeigh >= branch.orderb :
          pos += 1
          leftNeighB = self.session.query(Branch).filter_by(parent_id = branch.parent_id).order_by('orderb').offset(pos-1).limit(1).first()
          leftNeigh = leftNeighB.orderb
      rightNeighB = self.session.query(Branch).filter_by(parent_id = branch.parent_id).order_by('orderb').offset(pos).limit(1).first()
      rightNeigh = rightNeighB.orderb
      addit = (rightNeigh - leftNeigh) / 2
      if int(addit) <= 1:
        self.reindexing_orderb(branch.parent_id)
        self.moveB(branch, parent_id, pos)
        return
      branch.orderb = int(leftNeigh + addit)
    else:
      raise NegativePosition(connection=self.session)
    self.session.commit()

  def _add(self, branch):
    self.session.add(branch)
    self.session.commit()
    self.moveB(branch, pos = -1)

  def _add_all(self, *branches):
    for curb in branches:
      self._add(curb)

  def remove(self, branch):
    self.session.delete(branch)
    self.session.commit()

  def getB(self, id):
    resB = self.session.query(Branch).filter_by(id=id).scalar()
    resB.tree = self
    return resB

  def getB_root(self):
    return self.getB(general.rootB_id)

  def getSubBs(self, branch):
    subbs = self.session.query(Branch).filter_by(parent_id=branch.id).order_by('orderb').all()
    for curb in subbs:
      curb.tree = self
    return subbs

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
  caption = Column(String, default='New branch')
  text = Column(String, default='New branch')
  main = Column(Boolean, default='False')
  folded = Column(Boolean, default='False')
  parent_id = Column(Integer, ForeignKey(id))
  orderb = Column(Integer, index=True, default=0)
  subbs = relationship('Branch',
    # cascade deletions
    cascade="all, delete-orphan",

    # many to one + adjacency list - remote_side
    # is required to reference the 'remote' 
    # column in the join condition.
    backref=backref("parent", remote_side=id),
    )

  def __init__(self, tree, caption='New branch', text='New branch', main=False, folded=False, parent=None, parent_id=general.rootB_id):
    self.tree = tree
    self.caption = caption
    self.text = text
    self.main = main
    self.folded = folded
    self.parent = parent
    self.parent_id = parent_id
    self.tree._add(self)

  def get_subbs(self):
    return self.tree.getSubBs(self)

  def __repr__(self):
    return self.caption

  def __str__(self):
    return self.caption


if __name__ == '__main__':

  # cleaning
  import forest
  try:
    with forest.Forest() as f:
      f.removeTree(general.testdb)
      f.plantTree(general.testdb)
  except forest.ForestException:
    print("Error: ForestException has occured")

  print("Test:")
  try:
    with Tree(general.testdb) as curtree:
      rootb = curtree.getB_root()

      # create branches for test
      b1 = Branch(tree=curtree, caption="branch1", parent=rootb)
      b2 = Branch(tree=curtree, caption="branch2", main=True, parent=rootb)
      b3 = Branch(tree=curtree, caption="branch3", main=True, parent=rootb)
      b11 = Branch(tree=curtree, caption="branch11", parent=b1)
      b12 = Branch(tree=curtree, caption="branch12", parent=b1)

      # moving
      b21 = Branch(tree=curtree, caption="branch21", main=True)
      curtree.moveB(b2, b21.id)

      b22 = Branch(tree=curtree, caption="branch22")
      b23 = Branch(tree=curtree, caption="branch23")
      curtree.moveB(b22, parent_id = b2.id)
      curtree.moveB(b23, parent_id = b2.id)

      curtree.moveB(b23, pos = 0)
      if b23.orderb != (3 * general.orderb_step):
        raise BaseException("Moving problem")
      curtree.moveB(b23)
      if b23.orderb != (7 * general.orderb_step):
        raise BaseException("Moving problem")

      b31 = Branch(tree=curtree, caption="branch31", parent=b3)
      b32 = Branch(tree=curtree, caption="branch32", parent=b3)
      b33 = Branch(tree=curtree, caption="branch33", parent=b3)
      curtree.moveB(b31, pos = 1)
      if b31.orderb != (2.5 * general.orderb_step):
        raise BaseException("Moving problem")

      # get branch
      rootb = curtree.getB_root()
      b1 = curtree.getB(2)

      # get fields
      b1.id
      b1.caption
      b1.text
      b1.main
      b1.folded
      b1.get_subbs()
      b12 = curtree.getB(b1.get_subbs()[0].id)
      b1.parent
      for curB in b1.get_subbs():
        curB.caption

      # changing
      b1.text = "TEST"
      curtree.remove(b1)

      # reindexing orderb
      b24 = Branch(tree=curtree, caption="branch24", parent=b2)
      b25 = Branch(tree=curtree, caption="branch25", parent=b2)

      b23.orderb = general.orderb_MAX
      curtree.moveB(b22)
      if b23.orderb != (4 * general.orderb_step) :
        raise BaseException("Reindexing problem")

      b24.orderb = b25.orderb - general.orderb_MIN
      curtree.moveB(b23, pos = 1)
      if b24.orderb != (1 * general.orderb_step) :
        raise BaseException("Reindexing problem")

  except BaseException as e:
    print(e)
    print("FAILD")
  else:
    print("OK")
