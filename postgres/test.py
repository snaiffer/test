#!/usr/bin/env python3.3
import psycopg2
import psycopg2.extras

try:
  conn = psycopg2.connect("dbname='testdb2' user='postgres' password='123456'")
except:
  print("Error: Could not connect to the database!")
else:
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

  conn.commit()
  cur.close()
  conn.close()
