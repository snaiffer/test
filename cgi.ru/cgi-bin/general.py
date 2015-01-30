#!/usr/bin/env python3
" Global settings and constants "

import re

rootB_id = 1

# for ordering branches
orderb_step = 1000000   # initial step in order field between branches. It's tidy connection with orderb_MAX. And influence on performance
orderb_MIN = 1
orderb_MAX = 2147000000 - orderb_step
#

dbtype = "postgresql"
dbaddr = "localhost"

dbadmin_db      = "postgres"
dbadmin_login   = "postgres"
dbadmin_passwd  = "123456"

dbuser_login   = "postgres"
dbuser_passwd  = "123456"

testdb = "basket"

def checkout(text):
  """ Checkout if "text" consist of alphabets and numbers otherwise """
  if text == re.sub("[^a-zA-Z0-9]", "", text) :
    return True
  return False


if __name__ == '__main__':
  print("Settings:")
  print("========================================")
  print("rootB_id = " + str(rootB_id))
  print()
  print("orderb_step = " + str(orderb_step))
  print("orderb_MIN = " + str(orderb_MIN))
  print("orderb_MAX = " + str(orderb_MAX))
  print()
  print("testdb = " + str(testdb))
  print("========================================")

  print("\nTests:")
  if checkout("asdf893") and checkout("345fgfsddf34fd") and not checkout(";sdf()sdf]\[\;/;sd"):
    print("OK")
  else:
    print("FAILD")
