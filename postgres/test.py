#!/usr/bin/env python3.3
import psycopg2
import psycopg2.extras

try:
  conn=psycopg2.connect("dbname='testdb2' user='postgres' password='123456'")
except psycopg2.Error:
  print("Error: Could not connect to the database!")
else:
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  try:
    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
  except psycopg2.Error:
    pass
  cur.close()
  conn.close()

try:
  conn=psycopg2.connect("dbname='testdb2' user='postgres' password='123456'")
except psycopg2.Error:
  print("Error: Could not connect to the database!")
else:
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

  try:
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
    conn.commit()
  except psycopg2.Error:
    print("Error: Couldn't execute the query!")

  cur.close()
  conn.close()
