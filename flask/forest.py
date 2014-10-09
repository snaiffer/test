#!/usr/bin/env python3.3

import general
import psycopg2
import psycopg2.extras
import tree

class Forest():
  """
  Manage the trees
  At an instance creation a connection to db will be established. You should "close_conn()" at the end
  """
  def __init__(self):
    self.__conn = None
    self._estable_con()

  def __del__(self):
    self.close_conn()

  def __enter__(self, *args):
    return self

  def __exit__(self, *args):
    self.close_conn()

  def _estable_con(self):
    """ Establish a connection to the db """
    try:
      self.__conn = psycopg2.connect(
          "dbname = '"    + str(general.dbadmin_db) +
          "' user='"      + str(general.dbadmin_login) +
          "' password='"  + str(general.dbadmin_passwd) +
          "'")
    except psycopg2.Error as e:
      raise dbConnectProblem(e)

  def close_conn(self):  
    """ Close the connection to the db """
    if self.__conn != None:
      self.__conn.close() 
      self.__conn = None

  def list(self):
    """ Return the list of trees' names """
    try:
      with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname <> 'postgres'")
        return [ row[0] for row in cur.fetchall() ]
    except psycopg2.Error as e:
      raise CantExecuteQ(e)

  def isExist(self, treename):
    """ find out if tree with such name exist """
    try:
      trees_names = self.list()
      trees_names.index(treename)
    except ValueError:
      return False
    return True

  def plantTree(self, treename = "NewTree"):
    """
    Create (plant) a new tree
    "treename" has to consist of alphabets and numbers
    """
    if not general.checkout(treename):
      raise BadName

    if self.isExist(treename):
      raise dbAlreadyExist

    try:
      with self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        self.__conn.set_isolation_level(0)
        cur.execute("CREATE DATABASE %s;" % treename) # arg was operated from SQL injections
      with tree.Tree(treename) as newtree:  
        newtree.init()
    except (psycopg2.Error, tree.TreeException) as e:
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


class ForestException(Exception):
  def __init__(self, err=None, connection=None):
    if hasattr(connection, 'rollback') and connection != None:
      connection.rollback()
    if hasattr(err, 'pgerror') and err.pgerror != None:
      print(str(err.pgerror))
  def _output(self, msg):    
    print("Forest: " + str(msg))

class dbConnectProblem(ForestException):
  def __init__(self, err=None, connection=None):
    ForestException.__init__(self, err, connection)
    self._output("Error: can't connect to the database!")

class BadName(ForestException):
  def __init__(self, err=None, connection=None):
    ForestException.__init__(self, err, connection)
    self._output("Error: bad name!")

class dbAlreadyExist(ForestException):
  def __init__(self, err=None, connection=None):
    ForestException.__init__(self, err, connection)
    self._output("Error: the db is already exist !")


if __name__ == '__main__':
  treename = "treemind2"

  print("Tests:")
  try:
    with Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
      forest.isExist(forest.list().index(treename))
  except ForestException:
    print("Error: ForestException has occured")
    print("FAILD")
  except:
    print("FAILD")
  else:
    print("OK")



