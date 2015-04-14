#!/usr/bin/env python3
""" Global settings and constants """

import re

rootBglobal_id = 1

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

#testdb = "basket"
testdb = "test"

def checkout(text):
  """ Checkout if "text" consist of alphabets and numbers otherwise """
  if text == re.sub("[^a-zA-Z0-9]", "", text) :
    return True
  return False

def str2bool(v):
  if v != None:
    return v.lower() in ("yes", "true", "t", "1")
  return v


if __name__ == '__main__':
  print("Settings:")
  print("========================================")
  print("rootBglobal_id = " + str(rootBglobal_id))
  print()
  print("orderb_step = " + str(orderb_step))
  print("orderb_MIN = " + str(orderb_MIN))
  print("orderb_MAX = " + str(orderb_MAX))
  print()
  print("testdb = " + str(testdb))
  print("========================================")

  print("\nTests:")
  try:
    import sys

    sys.stdout.write("  ) Checkout function:\t")
    if not (checkout("asdf893") and checkout("345fgfsddf34fd") and not checkout(";sdf()sdf]\[\;/;sd")):
      raise BaseException("Checkout function of 'text' has failed!")
    print('OK')

    sys.stdout.write("  ) str2bool function:\t")
    if not (str2bool('yes') == True and str2bool('true') == True and str2bool('t') == True and str2bool('1') == True and str2bool('False') == False and str2bool(None) == None):
      raise BaseException("str2bool function has failed!")
    print('OK')
  except BaseException as e:
    print(e)
    print("\nSummary:\tFAILD")
  else:
    print("\nSummary:\tOK")
