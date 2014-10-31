#!/usr/bin/env python3.2

treename = "treemind2" #

import general
import forest as f
import tree as t
import branch as b

import json

def for_test():
  try:
    with f.Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
  except f.ForestException:
    print("Error: ForestException has occured")

  try:
    with t.Tree(treename) as tree:
      b1 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1', 'folded' : False})
      b2 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch2'})
      b11 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch11'})
      b12 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch12', 'folded' : True})
      b121 = tree.insertB({'parent_id' : b12.id, 'text' : 'branch121'})
      b122 = tree.insertB({'parent_id' : b12.id, 'text' : 'branch122'})
      b123 = tree.insertB({'parent_id' : b12.id, 'text' : 'branch123'})
  except t.TreeException:  
    print("Error: TreeException has occured")


import cgi
for_test()

form = cgi.FieldStorage()
id = form.getvalue('id', general.rootB_id)


try:
  with t.Tree(treename) as tree:
    print(tree.getB(id).text)
except b.BranchException:  
  print("Error: BranchException has occured")
except t.TreeException:  
  print("Error: TreeException has occured")

