#!/usr/bin/env python3.2

treename = "treemind2" #

import general
import forest as f
import tree as t


"""
def treemind(id, command, text=None):
  try:
    with t.Tree(treename) as tree:
      if command == "get_text":
        return tree.get_text(id)
      if command == "update_text":
        tree.update_text(id, text)
        return tree.get_text(id)
  except t.TreeException:  
    print("Error: TreeException has occured")
"""

def for_test():
  try:
    with f.Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
  except f.ForestException:
    print("Error: ForestException has occured")

  try:
    with t.Tree(treename) as tree:
      tree.insertB(general.rootB_id, 'branch1')
      tree.insertB(general.rootB_id, 'branch2')
      tree.insertB(2, 'branch11')
      tree.insertB(2, 'branch12')
  except t.TreeException:  
    print("Error: TreeException has occured")


import cgi
for_test()

form = cgi.FieldStorage()
id = form.getvalue('id')

print("Content-Type: text/html\n") 
try:
  with t.Tree(treename) as tree:



print("\
[{\
    \"id\":1,\"text\":\"Root node\",\"children\":[\
          {\"id\":2,\"text\":\"Child node 1\", \"children\" : true},\
          {\"id\":3,\"text\":\"Child node 2\"}\
      ]\
}]\
")


"""
name = form.getvalue('fname')
print("Name of the user is: " + str(name) + "<br>")


try:
  with t.Tree(treename) as tree:
    print()
    if command == "get_text":
      return tree.get_text(id)
    if command == "update_text":
      tree.update_text(id, text)
      return tree.get_text(id)
except t.TreeException:  
  print("Error: TreeException has occured")

"""



