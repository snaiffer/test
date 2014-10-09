#!/usr/bin/env python3.3

import general
import psycopg2
import psycopg2.extras

def plantTree(dbname = "NewTree"):
  dbname.replace(" ", "")
  dbname.replace(";", "")
  try:
    with psycopg2.connect("user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        """ Create db """
        try:
          conn.set_isolation_level(0)
          cur.execute("CREATE DATABASE %s;" % dbname) # arg was operated from SQL injections
        except psycopg2.Error as e:
          print("Error: Couldn't create the database!")
          print(str(e.pgerror))

  except psycopg2.Error as e:
    print("Error: During working with the database!")
    print(str(e.pgerror))

  try:
    with psycopg2.connect("dbname='%s' user='postgres' password='123456'" % dbname) as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        """ Create tables """
        try:
          cur.execute("CREATE TABLE branches (id serial PRIMARY KEY, caption text, text text, main bool, subB_id int[], parent_id int);")
          conn.commit()
        except psycopg2.Error:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))

        """ Create rootBranch """
        insertB(dbname, 1, dbname, main = True)

  except psycopg2.Error as e:
    print("Error: During working with the database!")
    print(str(e.pgerror))

def create_caption(text):
  result = text
  if len(result) > general.MAX_captionLen :
    return result[0:general.MAX_captionLen] + "..."
  else :
    return result

def insertB(dbname = "NewTree", parent_id = 1, text = "Unname", main = False):
  try:
    with psycopg2.connect("dbname='" + dbname + "' user='postgres' password='123456'") as conn:
      with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
          cur.execute("INSERT INTO branches (caption, text, main, subB_id, parent_id) VALUES (%s,%s,%s,%s,%s)", (text,create_caption(text),main,[],parent_id) )
          conn.commit()
        except psycopg2.Error as e:
          conn.rollback()
          print("Error: Couldn't execute the query!")
          print(str(e.pgerror))

  except psycopg2.Error:
    print("Error: During working with the database!")

if __name__ == '__main__':
  plantTree("treemind2")



