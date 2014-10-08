#!/usr/bin/env python3.3
import psycopg2
import psycopg2.extras

try:
  with psycopg2.connect("dbname='testdb2' user='postgres' password='123456'") as conn:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
      try:
        cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        conn.commit()
      except psycopg2.Error:
        conn.rollback()
        pass

      try:
        num = int(input("Enter 'num': "))
        data = str(input("Enter 'data': "))
        SQL = "INSERT INTO test (num, data) VALUES (%s, %s)"
        data = (num, data)
        cur.execute( SQL % data )
        conn.commit()
      except psycopg2.Error as e:
        conn.rollback()
        print("Error: Couldn't execute the query!")
        print(str(e.pgerror))

      try:
        cur.execute("SELECT * from test")
        conn.commit()
      except psycopg2.Error:
        conn.rollback()
        print("Error: Couldn't execute the query!")
      else:
        rows = cur.fetchall()
        print("\nRows: \n")
        for row in rows:
          print( " " + str(row['num']) + "\t" + str(row['data']))

except psycopg2.Error:
  print("Error: During working with the database!")
