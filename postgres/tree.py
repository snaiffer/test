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
          print("Error: Couldn't create the database!")
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

def insertB(treename, parent_id = general.rootB_id, text = "Unname", main = False):
  """ Create a new branch """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
          cur.execute("INSERT INTO branches (caption, text, main, subB_id, parent_id) VALUES (%s,%s,%s,%s,%s)", (text,create_caption(text),main,[],parent_id) )
          conn.commit()
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))
          raise CantExecute

  except psycopg2.Error:
    print("Error: During working with the database!")
    raise CantExecute

def removeB(treename, id):  
  """ Remove a branch by id """
  try:
    with psycopg2.connect("dbname='" + treename + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
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
  except CantExecute:
    print("Error: The operation hasn't been executed")

  try:
    removeB(treename, 2)
  except CantExecute:
    print("Error: The operation hasn't been executed")



