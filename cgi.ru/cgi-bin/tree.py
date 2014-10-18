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
    self.accessibleAttrs = ("caption", "text", "main", "folded")

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
        cur.execute("CREATE TABLE branches (id serial PRIMARY KEY, caption text, text text, main bool, folded bool, subbs_id int[], parent_id int);")
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        """ Create rootBranch """
        self.insertB(None, "root", main = True)

  def _create_caption(self, text):
    result = text
    if len(result) > general.MAX_captionLen :
      return result[0:general.MAX_captionLen] + "..."
    else :
      return result

  def _add_subb(self, b_id, subb_id):
    """ Add the subbranch with "subb_id" to the branch with "b_id"  """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("update branches set subbs_id = array_append(subbs_id,%s) where id = %s;", (subb_id,b_id) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)


  def insertB(self, parent_id = general.rootB_id, text = "Unname", main = False, folded = False):
    """ 
    Create a new branch 
    return id of the branch
    """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        """ add a record """
        cur.execute("INSERT INTO branches (caption, text, main, folded, subbs_id, parent_id) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id", (text, self._create_caption(text),main,folded,[],parent_id) )

        """ add id of the record to the parent """
        b_id = cur.fetchone()['id']
        if parent_id != None:
          self._add_subb(parent_id, b_id)

        self.conn.commit()
        return b_id
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)

  def get_subbs(self, id):  
    """ Return list of subbranches of the branch with id """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT subbs_id FROM branches WHERE id = %s", (id,) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        return cur.fetchone()['subbs_id']

  def get_parent(self, id):  
    """ Return "parent_id" of the branch with id """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT parent_id FROM branches WHERE id = %s", (id,) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        return cur.fetchone()['parent_id']

  def get_text(self, id):  
    """ Return "text" of the branch with id """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("SELECT text FROM branches WHERE id = %s", (id,) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)
      else:
        return cur.fetchone()['text']

  def update_text(self, id, text):  
    """ Update "text" of the branch with id """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("UPDATE branches set text = %s, caption = %s WHERE id = %s", (text,self._create_caption(text), id) )
        self.conn.commit()
      except psycopg2.Error as e:
        raise CantExecuteQ(e, self.conn)

  def removeB(self, id):  
    """ Remove a branch by id """
    with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        """ remove subbranches """
        subbs = self.get_subbs(id)
        if subbs != None:
          for cur_subb in subbs:
            self.removeB(cur_subb)

        """ remove id of the branch from parent """
        parent_id = self.get_parent(id)
        cur.execute("update branches set subbs_id = array_remove(subbs_id, %s) where id = %s", (id, parent_id))
        
        """ remove the record """
        cur.execute("DELETE FROM branches WHERE id = %s", (id,) )

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

  def get_rootb(self):
    """ return Branch() of root if it's exist otherwise return None """
    return self.get_b(general.rootB_id)

  def get_b(self, id = general.rootB_id):
    """ return Branch() with the "id" if it's exist otherwise return None """
    if self._isExist_b(id):
      return branch.Branch(self, id)
    return None





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

class idNotUnique(TreeException):
  def __init__(self, err=None, connection=None):
    TreeException.__init__(self, err, connection)
    self._output("Error: id isn't unique!")


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
      tree.insertB(general.rootB_id, 'branch1')
      tree.insertB(general.rootB_id, 'branch2')
      tree.insertB(2, 'branch11')
      tree.insertB(2, 'branch12')
      tree.get_text(2)
      tree.update_text(3, 'b2')

      if [4,5] != tree.get_subbs(2):
        raise
      tree.removeB(5)
      if [4,] != tree.get_subbs(2):
        raise

      if not tree._isExist_b(1):
        print("FAILD")
      if tree._isExist_b(1000):
        print("FAILD")
      
      rootb = tree.get_rootb()
      if rootb == None or rootb.id != general.rootB_id:
        print("FAILD")
      b1 = tree.get_b(2)
      if rootb == None or b1.id != 2:
        print("FAILD")
      b1000 = tree.get_b(1000)
      if b1000 != None:
        print("FAILD")

  except TreeException:  
    print("Error: TreeException has occured")
    print("FAILD")
  else:
    print("OK")



