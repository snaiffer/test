#!/usr/bin/env python3.2

treename = "treemind2" #

import general
import forest as f
import tree as t

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
      tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1'})
      tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch2'})
      tree.insertB({'parent_id' : 2, 'text' : 'branch11'})
      tree.insertB({'parent_id' : 2, 'text' : 'branch12'})
  except t.TreeException:  
    print("Error: TreeException has occured")


import cgi
for_test()

form = cgi.FieldStorage()
id = form.getvalue('id')

print("Content-Type: text/html\n") 

"""
def getDict(branch):
  dict = {}
  dict['id'] = branch.id
  dict['text'] = branch.caption
  if branch.subbs_id != [] :
    dict['state'] = {}
    dict['state']['opened'] = branch.folded ^ True
    if dict['state']['opened'] == True:
      dict['children'] = []
      dict['children'].append()
    else:
      dict['children'] = True
  return dict  

try:
  with t.Tree(treename) as tree:
    print(json.dumps(getDict(tree.getB_root())))
except BranchException:  
  print("Error: BranchException has occured")
except tree.TreeException:  
  print("Error: TreeException has occured")
"""



print("\
[{\
\"id\":1,\"text\":\"Root node\", \"state\" : {\"opened\" : true } ,\"children\":[\
          {\"id\":2,\"text\":\"Child node 1\", \"children\" : true},\
          {\"id\":3,\"text\":\"Child node 2\"}\
      ]\
}]\
")


