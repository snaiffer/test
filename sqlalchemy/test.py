#!/usr/bin/env python3.2

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Parent(Base):
  __tablename__ = 'parent'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  children = relationship("Child", backref="parent123")
  #children = relationship("Child")
  def __repr__(self):
    return self.name

class Child(Base):
  __tablename__ = 'child'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  parent_id = Column(Integer, ForeignKey('parent.id'))
  def __repr__(self):
    return self.name

if __name__ == '__main__':
  engine = create_engine("postgresql://postgres:123456@localhost/sqlalchemy")

  Base.metadata.create_all(engine)

  Session = sessionmaker(bind=engine)
  session = Session()

  p = Parent(name="Alex")
  c = Child(name="Danilov")
  p.children = [c,]         # Here! we use "backref"
  
  print(p.children)
  print(c.parent123)
  #session.add(p)
  #session.commit()


