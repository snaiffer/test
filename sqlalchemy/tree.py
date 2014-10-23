#!/usr/bin/env python3.2

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TreeNode(Base):
  __tablename__ = 'tree'
  id = Column(Integer, primary_key=True)
  parent_id = Column(Integer, ForeignKey(id))
  name = Column(String)

  children = relationship('TreeNode',
    # cascade deletions
    cascade="all, delete-orphan",

    # many to one + adjacency list - remote_side
    # is required to reference the 'remote' 
    # column in the join condition.
    backref=backref("parent", remote_side=id),
    )

  def __init__(self, name, parent=None):
    self.name = name
    self.parent = parent

  def __repr__(self):
    return self.name

  def __str__(self):
    return self.name


if __name__ == '__main__':
  engine = create_engine("postgresql://postgres:123456@localhost/sqlalchemy")

  Base.metadata.create_all(engine)

  Session = sessionmaker(bind=engine)
  session = Session()

  node = TreeNode("root")
  TreeNode("branch1", parent=node)
  TreeNode("branch2", parent=node)

  session.add(node)
  session.commit()

  print()
  print(node.name)
  print(node.children)
  for i in node.children:
    print(i.name)

  session.delete(node)
  session.commit()

  print()
  node = session.query(TreeNode).filter_by(name='root').first()
  print(node)

