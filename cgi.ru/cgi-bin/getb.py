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
      b1 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1', 'folded' : True})
      #b1 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1'})
      b2 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch2'})
      b11 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch11'})
      b12 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch12'})
  except t.TreeException:  
    print("Error: TreeException has occured")


import cgi
for_test()

form = cgi.FieldStorage()
id = form.getvalue('id')

print("Content-Type: text/html\n") 

#logfile = open('log', 'w')
#print('', file=logfile)
#print(str(id), file=logfile)


def getDict(branch):
  dict = {}
  dict['id'] = branch.id
  dict['text'] = branch.caption
  if branch.subbs_id != [] :
    dict['state'] = {}
    dict['state']['opened'] = branch.folded ^ True
    if dict['state']['opened'] == True:
      dict['children'] = []
      for cur_subb in branch.subbs:
        dict['children'].append(getDict(cur_subb))
    else:
      dict['children'] = True
  return dict  

def getList_subbsOf(branch):
  list = []
  if branch.subbs_id != [] :
    for cur_subb in branch.subbs:
      list.append(getDict(cur_subb))
  return list    

try:
  with t.Tree(treename) as tree:
    if id == None or id == general.rootB_id:
      print(json.dumps(getDict(tree.getB(general.rootB_id))))
    else:  
      print(json.dumps(getList_subbsOf(tree.getB(id))))
except b.BranchException:  
  print("Error: BranchException has occured")
except t.TreeException:  
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
"""

#logfile.close()

