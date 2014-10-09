#!/usr/bin/env python3
" Global settings and constants "

import re

MAX_captionLen = 29 #30
rootB_id = 1


dbadmin_db      = "postgres"
dbadmin_login   = "postgres"
dbadmin_passwd  = "123456"

dbuser_login   = "postgres"
dbuser_passwd  = "123456"

def checkout(text):
  """ Checkout if "text" consist of alphabets and numbers otherwise """
  if text == re.sub("[^a-zA-Z0-9]", "", text) :
    return True
  return False


if __name__ == '__main__':
  print("MAX_captionLen = " + str(MAX_captionLen))
  print("rootB_id = " + str(rootB_id))

  print("\nTests:")
  if checkout("asdf893") and checkout("345fgfsddf34fd") and not checkout(";sdf()sdf]\[\;/;sd"):
    print("OK")
  else:  
    print("FAILD")
