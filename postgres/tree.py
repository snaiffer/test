#!/usr/bin/env python3.3

import general
import psycopg2
import psycopg2.extras
import re


class Forest():
  def __init__(self):
    self.__estable_con()

  def __del__(self):
    self.close_con()

  def __enter__(self, *args):
    return self

  def __exit__(self, *args):
    self.close_con()

  def __estable_con(self):
    try:
      self.__conn = psycopg2.connect("user='postgres' password='123456'")
    except psycopg2.Error as e:
      raise dbConnectProblem(e)

  def close_con(self):  
    self.__conn.close()

  def __checkout(self, treename):
    """ treename has to consist of alphabets and numbers otherwise "BadName" will be raised """
    if treename != re.sub("[^a-zA-Z0-9]","",treename) :
      raise BadName

  def list(self):
    """ Return the list of trees' names """
    try:
      with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname <> 'postgres'")
        return [ row[0] for row in cur.fetchall() ]
    except psycopg2.Error as e:
      raise CantExecuteQ(e)

  def isExist(self, treename):
    """ find out if tree with such name already exist """
    try:
      trees_names = self.list()
      trees_names.index(treename)
    except ValueError:
      return False
    return True

  def plantTree(self, treename = "NewTree"):
    """
    Create (plant) a new tree
    treename has to consist of alphabets and numbers
    """
    self.__checkout(treename)

    if self.isExist(treename):
      raise dbAlreadyExist

    try:
      with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        self.__conn.set_isolation_level(0)
        cur.execute("CREATE DATABASE %s;" % treename) # arg was operated from SQL injections
      with Tree(treename) as newtree:  
        newtree.init()
    except (psycopg2.Error, TreeException) as e:
      self.removeTree(treename)
      raise CantExecuteQ(e)

  def removeTree(self, treename = "NewTree"):
    """ Remove the tree """
    if not self.isExist(treename):
      return

    try:
      with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        self.__conn.set_isolation_level(0)
        cur.execute("DROP DATABASE %s;" % treename) # arg was operated from SQL injections
    except psycopg2.Error as e:
      raise CantExecuteQ(e)



class Tree():
  def __init__(self, treename):
    if not Forest().isExist(treename):
      raise TreeIsntExist
    self.__treename = treename
    self.__estable_con()

  def __del__(self):
    self.close_con()

  def __enter__(self, *args):
    return self

  def __exit__(self, *args):
    self.close_con()

  def __estable_con(self):
    try:
      self.__conn = psycopg2.connect("dbname='" + self.__treename + "' user='postgres' password='123456'")
    except psycopg2.Error as e:
      raise dbConnectProblem(e)

  def close_con(self):  
    self.__conn.close()

  def init(self):
    with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      """ Create tables """
      try:
        cur.execute("CREATE TABLE branches (id serial PRIMARY KEY, caption text, text text, main bool, subb_id int[], parent_id int);")
        self.__conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.__conn)
      else:
        """ Create rootBranch """
        self.insertB(None, treename, main = True)

  def __create_caption(self, text):
    result = text
    if len(result) > general.MAX_captionLen :
      return result[0:general.MAX_captionLen] + "..."
    else :
      return result

  def __add_subb(self, b_id, subb_id):
    """ Add the subbranch with "subb_id" to the branch with "b_id"  """
    with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("update branches set subb_id = array_append(subb_id,%s) where id = %s;", (subb_id,b_id) )
        self.__conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.__conn)


  def insertB(self, parent_id = general.rootB_id, text = "Unname", main = False):
    """ 
    Create a new branch 
    return id of the branch
    """
    with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        """ add a record """
        cur.execute("INSERT INTO branches (caption, text, main, subB_id, parent_id) VALUES (%s,%s,%s,%s,%s) RETURNING id", (text, self.__create_caption(text),main,[],parent_id) )

        """ add id of the record to the parent """
        b_id = cur.fetchone()['id']
        if parent_id != None:
          self.__add_subb(parent_id, b_id)

        self.__conn.commit()
        return b_id
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.__conn)

  def get_subbs(self, id):  
    """ Return list of subbranches of the branch with id """
    with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT subb_id FROM branches WHERE id = %s", (id,) )
        self.__conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.__conn)
      else:
        return cur.fetchone()['subb_id']

  def get_parent(self, id):  
    """ Return "parent_id" of the branch with id """
    with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT parent_id FROM branches WHERE id = %s", (id,) )
        self.__conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.__conn)
      else:
        return cur.fetchone()['parent_id']

  def removeB(treename, id):  
    """ Remove a branch by id """
    with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        """ remove subbranches """
        subbs = get_subbs(treename, id)
        if subbs != None:
          for cur_subb in subbs:
            removeB(treename, cur_subb)

        """ remove id of the branch from parent """
        parent_id = get_parent(treename, id)
        cur.execute("update branches set subb_id = array_remove(subb_id, %s) where id = %s", (id, parent_id))
        
        """ remove the record """
        cur.execute("DELETE FROM branches WHERE id = %s", (id,) )

        self.__conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.__conn)


class dbAlreadyExist(Exception):
  pass

class TreeException(Exception):
  pass

class dbConnectProblem(Exception):
  def __init__(self, err=None):
    print("Error: can't connect to the database!")
    if err:
      print(str(err.pgerror))
  pass

class BadName(Exception):
  pass

class CantExecuteQ(TreeException):
  def __init__(self, err=None, connection=None):
    print("Error: can't execute the query!")
    if hasattr(err, 'pgerror'):
      print(str(err.pgerror))
    if hasattr(connection, 'rollback'):
      connection.rollback()

class TreeIsntExist(TreeException):
  pass

if __name__ == '__main__':
  treename = "treemind2"

  try:
    with Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
  except dbAlreadyExist:
    print("Error: the db with such name is already exist!")
  except dbConnectProblem:
    print("Error: can't connect to the db")
  except CantExecuteQ:  
    print("Error: can't execute the operation")

  try:
    with Tree(treename) as tree:
      tree.insertB(general.rootB_id, 'branch1')
      tree.insertB(general.rootB_id, 'branch2')
      tree.insertB(2, 'branch11')
      tree.insertB(2, 'branch12')
  except CantExecuteQ:  
    print("Error: can't execute the operation")



  """
  try: 
    removeTree(treename)
  except CantExecuteQ:
    print("Error: Can't remove the tree. May be it isn't exist")

  try: 
    plantTree(treename)
  except CantExecuteQ:
    print("Error: Can't plant the tree. May be a tree with the same name already exist")

  try:
    insertB(treename, general.rootB_id, "branch1", True)
    insertB(treename, 2, "branch11", True)
    insertB(treename, 2, "branch12", True)
    insertB(treename, 3, "branch111", True)
  except CantExecuteQ:
    print("Error: The operation hasn't been executed")

  try:
    removeB(treename, 2)
  except CantExecuteQ:
    print("Error: The operation hasn't been executed")
  """



