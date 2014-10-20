#!/usr/bin/env python3.2

import general
import psycopg2
import psycopg2.extras

import tree

baseAttrs = ("hostTree", "conn", "id")

class Branch():
  def __init__(self, tree, id):
    """ You have to add all names of attrs to "baseAttrs" tuple """
    self.hostTree = tree
    self.conn = tree.conn
    self.id = id

  def __getattr__(self, field):
    if not field in self.hostTree.branchesFields :
      raise AttributeError
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT " + field + " FROM branches WHERE id = %s", (self.id,) ) # arg was operated from SQL injections
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        return cur.fetchone()[field]

  def __setattr__(self, field, value):
    if field in baseAttrs:
      super().__setattr__(field, value)
      return

    if not field in self.hostTree.branchesFields :
      raise AttributeError
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("UPDATE branches set " + field + " = %s WHERE id = %s", (value, self.id) ) # arg was operated from SQL injections
        if field == "text":
          cur.execute("UPDATE branches set caption = %s WHERE id = %s", (self._create_caption(value), self.id) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)

  def _create_caption(self, text):
    result = text
    if len(result) > general.MAX_captionLen :
      return result[0:general.MAX_captionLen] + "..."
    else :
      return result

  def get_parentB(self):  
    """ Return a parent branch of the current branch """
    return self.hostTree.getB(self.parent_id)

  def remove(self):
    """ remove the current branch """
    self.hostTree.removeB(self.id)


class BranchException(Exception):
  def __init__(self, err=None, connection=None):
    if hasattr(connection, 'rollback') and connection != None:
      connection.rollback()
    if hasattr(err, 'pgerror') and err.pgerror != None:
      print(str(err.pgerror))
  def _output(self, msg):    
    print(str(msg))

class CantExecuteQ(BranchException):
  def __init__(self, err=None, connection=None):
    BranchException.__init__(self, err, connection)
    self._output("Error: can't execute the query!")


if __name__ == '__main__':
  treename = "treemind2"

  # cleaning
  import forest
  try:
    with forest.Forest() as f:
      f.removeTree(treename)
      f.plantTree(treename)
  except forest.ForestException:
    print("Error: ForestException has occured")

  print("Test:")
  try:
    with tree.Tree(treename) as t:
      # create test branches
      t.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1'})
      t.insertB({'parent_id' : general.rootB_id, 'text' : 'branch2'})
      t.insertB({'parent_id' : 2, 'text' : 'branch11'})
      t.insertB({'parent_id' : 2, 'text' : 'branch12'})

      # get branch
      rootb = t.getB_root()
      b1 = t.getB(2)
      b2 = Branch(t, 3)

      # get fields
      b1.id
      b1.caption
      b1.text
      b1.main
      b1.folded
      subbs_list = b1.subbs_id
      b3 = t.getB(b1.subbs_id[0])
      if b1.get_parentB() == None:
        print("FAILD")

      # changing
      b1.text = "changed text"
      b1.subbs_id = [10,11,12]
      b1.subbs_id = [4,5]
      b1.remove()

  except BranchException:  
    print("Error: BranchException has occured")
    print("FAILD")
  except tree.TreeException:  
    print("Error: TreeException has occured")
    print("FAILD")
  else:
    print("OK")
