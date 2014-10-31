#!/usr/bin/env python3.2

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Branch(Base):
  __tablename__ = 'branches'
  id = Column(Integer, primary_key=True)
  caption = Column(String, default='New branch')
  text = Column(String, default='New branch')
  main = Column(Boolean, default='False')
  folded = Column(Boolean, default='False')
  parent_id = Column(Integer, ForeignKey(id))
  subbs = relationship('Branch',
    # cascade deletions
    cascade="all, delete-orphan",

    # many to one + adjacency list - remote_side
    # is required to reference the 'remote' 
    # column in the join condition.
    backref=backref("parent", remote_side=id),
    )

  def __init__(self, caption='New branch', text='New branch', main=False, folded=False, parent=None, parent_id=None):
    self.caption = caption
    self.text = text
    self.main = main
    self.folded = folded
    self.parent = parent
    self.parent_id = parent_id

  def add_subb(self, branch):
    """ Add a new subbranch """
    branch.parent = self

  def add_subbs(self, branches):
    """ Add a new subbranches """
    for curb in branches:
      curb.parent = self

  def __repr__(self):
    return self.caption

  def __str__(self):
    return self.caption

class Tree():
  def __init__(self, name, session = None):
    self.name = name
    self.session = session

  def __enter__(self, *args):
    if self.session:
      return self.session
    engine = create_engine("postgresql://postgres:123456@localhost/" + self.name)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    self.session = Session()
    return self

  def __exit__(self, *args):
    self.session.commit()
    self.session.close()

  def add(self, branch):
    self.session.add(branch)
    self.session.commit()

  def remove(self, branch):
    self.session.delete(branch)
    self.session.commit()
    
  def getB(self, id):  
    return self.session.query(Branch).filter_by(id=id).scalar()

  def getB_root(self):
    return self.getB(1)


if __name__ == '__main__':
  with Tree("sqlalchemy") as curtree:
    rootb = Branch(caption = "root", text = "root", main = True)

    # create branches for test
    b1 = Branch(caption="branch1", parent=rootb)
    b2 = Branch(caption="branch2", parent=rootb)
    b11 = Branch(caption="branch11", parent=b1)
    b12 = Branch(caption="branch12", parent=b1)

    b21 = Branch(caption="branch21")
    b2.add_subb(b21)

    b22 = Branch(caption="branch22")
    b23 = Branch(caption="branch23")
    b2.add_subbs([b22, b23])

    curtree.add(rootb)

    # get branch
    rootb = curtree.getB_root()
    b1 = curtree.getB(2)

    # get fields
    b1.id
    b1.caption
    b1.text
    b1.main
    b1.folded
    b1.subbs
    b12 = curtree.getB(b1.subbs[0].id)
    b1.parent
    for curB in b1.subbs:
      curB.caption

    # changing
    b1.text = "TEST"
    curtree.remove(b1)
    curtree.remove(b2)

