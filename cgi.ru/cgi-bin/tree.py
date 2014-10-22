#!/usr/bin/env python3.2

import general
import psycopg2
import psycopg2.extras

import branch

class Tree():
  def __init__(self, treename):
    self.conn = None
    if not general.checkout(treename):
      raise BadName
    self.__treename = treename
    self._estable_con()
    self.branchesFields = ("id", "caption", "text", "main", "folded", "subbs_id", "parent_id")

  def __del__(self):
    self.close_con()

  def __enter__(self, *args):
    return self

  def __exit__(self, *args):
    self.close_con()

  def _estable_con(self):
    """ Establish a connection to the db """
    try:
      self.conn = psycopg2.connect(
          "dbname = '"    + str(self.__treename) +
          "' user='"      + str(general.dbuser_login) +
          "' password='"  + str(general.dbuser_passwd) +
          "'")
    except psycopg2.Error as e:
      raise dbConnectProblem(e)

  def close_con(self):  
    """ Close the connection to the db """
    if self.conn != None:
      self.conn.close()
      self.conn = None

  def init(self):
    """ Initialize tables and create root branch in the new tree """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      """ Create tables """
      try:
        cur.execute("CREATE TABLE branches (\
            id serial PRIMARY KEY, \
            caption text default 'New branch', \
            text text default 'New branch', \
            main bool default False, \
            folded bool default False, \
            subbs_id int[] default '{}', \
            parent_id int default 1);")
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        """ Create rootBranch """
        self.insertB({'parent_id' : None, 'text' : 'root', 'main' : True})


  def insertB(self, kwargs):
    """ 
    Insert a new branch 
    Return the new branch in case of success
    """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        """ create an empty branch """
        cur.execute("INSERT INTO branches DEFAULT VALUES RETURNING id")
        b_id = cur.fetchone()['id']
        self.conn.commit()
        newB = self.getB(b_id)
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        try:
          """ fill in the new branch """
          for key in kwargs :
            newB.__setattr__(key, kwargs[key])

          if newB.parent_id != None:
            """ couple the new branch to the tree """
            parentB = self.getB(newB.parent_id)
            parentB.subbs_id = parentB.subbs_id + [newB.id]

          return newB  
        except:
          self.removeB(newB.id)
          raise CantExecuteQ()

  def removeB(self, b_id):
    """ remove the branch with "b_id" id """

    branch = self.getB(b_id)
    """ remove subbranches """
    for curB_id in branch.subbs_id:
      self.removeB(curB_id)

    """ remove id of the branch from parent """
    b_subbs_id = self.getB(branch.parent_id).subbs_id
    b_subbs_id.remove(branch.id)
    self.getB(branch.parent_id).subbs_id = b_subbs_id

    """ remove the record """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("DELETE FROM branches WHERE id = %s", (branch.id,) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)

  def _isExist_b(self, id):  
    """ 
    find out if the branch with such id is exist. 
    Return "True" of "False". In case of multi the same ids it'll raise idNotUnique
    """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT id FROM branches WHERE id = %s", (id,) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        rows_len = len(cur.fetchall())
        if rows_len == 0:
          return False
        elif rows_len == 1:
          return True
        else:
          raise idNotUnique

  def getB_root(self):
    """ return Branch() of root if it's exist otherwise raise branchNotExist """
    return self.getB(general.rootB_id)

  def getB(self, id = general.rootB_id):
    """ return Branch() with the "id" if it's exist otherwise raise branchNotExist """
    if self._isExist_b(id):
      return branch.Branch(self, id)
    raise branchNotExist


class TreeException(Exception):
  def __init__(self, err=None, connection=None):
    if hasattr(connection, 'rollback') and connection != None:
      connection.rollback()
    if hasattr(err, 'pgerror') and err.pgerror != None:
      print(str(err.pgerror))
  def _output(self, msg):    
    print(str(msg))

class dbConnectProblem(TreeException):
  def __init__(self, err=None, connection=None):
    TreeException.__init__(self, err, connection)
    self._output("Error: can't connect to the database!")

class CantExecuteQ(TreeException):
  def __init__(self, err=None, connection=None):
    TreeException.__init__(self, err, connection)
    self._output("Error: can't execute the query!")

class BadName(TreeException):
  def __init__(self, err=None, connection=None):
    TreeException.__init__(self, err, connection)
    self._output("Error: bad name!")

class idnotunique(TreeException):
  def __init__(self, err=None, connection=None):
    TreeException.__init__(self, err, connection)
    self._output("Error: id isn't unique!")

class branchNotExist(TreeException):
  def __init__(self, err=None, connection=None):
    TreeException.__init__(self, err, connection)
    self._output("Error: branch isn't exist!")


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
    with Tree(treename) as tree:
      b1 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1'})
      b2 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch2'})
      b11 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch11'})
      b12 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch12'})

      if not tree._isExist_b(1):
        print("FAILD")
      if tree._isExist_b(1000):
        print("FAILD")
      
      rootb = tree.getB_root()
      b1 = tree.getB(2)

      tree.removeB(2)
      if tree.getB_root().subbs_id != [3,]:
        print("FAILD")

  except TreeException:  
    print("Error: TreeException has occured")
    print("FAILD")
  else:
    print("OK")

