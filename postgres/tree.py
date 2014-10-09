#!/usr/bin/env python3.3

import general
import psycopg2
import psycopg2.extras
import re

def plantTree(treename = "NewTree"):
  """
  Create (plant) a new tree
  treename has to consist of alphabets and numbers
  """
  treename = re.sub("[^a-zA-Z0-9]","",treename)
  try:
    with psycopg2.connect("user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        """ Create db """
        try:
          conn.set_isolation_level(0)
          cur.execute("CREATE DATABASE %s;" % treename) # arg was operated from SQL injections
        except psycopg2.Error as e:
          print("Error: Couldn't create the database!")
          print(str(e.pgerror))
          raise CantExecute

  except psycopg2.Error as e:
    print("Error: During working with the database!")
    print(str(e.pgerror))
    raise CantExecute

  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        """ Create tables """
        try:
          cur.execute("CREATE TABLE branches (id serial PRIMARY KEY, caption text, text text, main bool, subb_id int[], parent_id int);")
          conn.commit()
        except psycopg2.Error:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute

        """ Create rootBranch """
        try:
          insertB(treename, general.rootB_id, treename, main = True)
        except CantExecute:
          raise CantExecute

  except psycopg2.Error as e:
    print("Error: During working with the database!")
    print(str(e.pgerror))
    raise CantExecute

def removeTree(treename = "NewTree"):
  """ Remove the tree """
  treename = re.sub("[^a-zA-Z0-9]","",treename)
  try:
    with psycopg2.connect("user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        """ Create db """
        try:
          conn.set_isolation_level(0)
          cur.execute("DROP DATABASE %s;" % treename) # arg was operated from SQL injections
        except psycopg2.Error as e:
          print("Error: Couldn't remove the database!")
          print(str(e.pgerror))
          raise CantExecute

  except psycopg2.Error as e:
    print("Error: During working with the database!")
    print(str(e.pgerror))
    raise CantExecute

def create_caption(text):
  result = text
  if len(result) > general.MAX_captionLen :
    return result[0:general.MAX_captionLen] + "..."
  else :
    return result

def add_subb(treename, b_id, subb_id):
  """ Add the subbranch with "subb_id" to the branch with "b_id"  """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
          cur.execute("update branches set subb_id = array_append(subb_id,%s) where id = %s;", (subb_id,b_id) )
          conn.commit()
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute

  except psycopg2.Error:
    print("Error: During working with the database!")
    raise CantExecute

def insertB(treename, parent_id = general.rootB_id, text = "Unname", main = False):
  """ 
  Create a new branch 
  return id of the branch
  """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
          """ add a record """
          cur.execute("INSERT INTO branches (caption, text, main, subB_id, parent_id) VALUES (%s,%s,%s,%s,%s) RETURNING id", (text,create_caption(text),main,[],parent_id) )

          """ add id of the record to the parent """
          b_id = cur.fetchone()['id']
          add_subb(treename, parent_id, b_id)

          conn.commit()
          return b_id
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute

  except psycopg2.Error:
    print("Error: During working with the database!")
    raise CantExecute

def get_subbs(treename, id):  
  """ Return list of subbranches of the branch with id """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
          cur.execute("SELECT subb_id FROM branches WHERE id = %s", (id,) )
          conn.commit()
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute
        else:
          return cur.fetchone()['subb_id']

  except psycopg2.Error:
    print("Error: During working with the database!")
    raise CantExecute

def get_parent(treename, id):  
  """ Return "parent_id" of the branch with id """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
          cur.execute("SELECT parent_id FROM branches WHERE id = %s", (id,) )
          conn.commit()
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute
        else:
          return cur.fetchone()['parent_id']

  except psycopg2.Error:
    print("Error: During working with the database!")
    raise CantExecute

def removeB(treename, id):  
  """ Remove a branch by id """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
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

          conn.commit()
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute

  except psycopg2.Error:
    print("Error: During working with the database!")
    raise CantExecute



class CantExecute(Exception):
  pass

class CantExecute(Exception):
  pass

if __name__ == '__main__':
  treename = "treemind2"

  try: 
    removeTree(treename)
  except CantExecute:
    print("Error: Can't remove the tree. May be it isn't exist")

  try: 
    plantTree(treename)
  except CantExecute:
    print("Error: Can't plant the tree. May be a tree with the same name already exist")

  try:
    insertB(treename, general.rootB_id, "branch1", True)
    insertB(treename, 2, "branch11", True)
    insertB(treename, 2, "branch12", True)
    insertB(treename, 3, "branch111", True)
  except CantExecute:
    print("Error: The operation hasn't been executed")

  try:
    removeB(treename, 3)
  except CantExecute:
    print("Error: The operation hasn't been executed")



