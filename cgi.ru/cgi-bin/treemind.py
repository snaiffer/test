#!/usr/bin/env python3.2

treename = "test" #

import general
from forest import Forest
from tree import Tree, Branch

import json

def for_test():
  try:
    with Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
  except ForestException:
    print("Error: ForestException has occured")

  with Tree(treename) as curtree:
    rootb = curtree.getB_root()

    # create branches for test
    b1 = Branch(caption="branch1", parent=rootb)
    b2 = Branch(caption="branch2", parent=rootb)
    b11 = Branch(caption="branch11", parent=b1)
    b12 = Branch(caption="branch12", parent=b1)

    b21 = Branch(caption="branch21")
    b2.add_subb(b21)

    b22 = Branch(caption="branch22")
    b23 = Branch(caption="branch23")
    b2.add_subbs([b22, b23])

    curtree.add(rootb)
  """
  try:
    with tree.Tree(treename) as tree:
      b1 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch1', 'folded' : False})
      b2 = tree.insertB({'parent_id' : general.rootB_id, 'text' : 'branch2'})
      b11 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch11'})
      b12 = tree.insertB({'parent_id' : b1.id, 'text' : 'branch12', 'folded' : True})
      b121 = tree.insertB({'parent_id' : b12.id, 'text' : 'branch121'})
      b122 = tree.insertB({'parent_id' : b12.id, 'text' : 'branch122'})
      b123 = tree.insertB({'parent_id' : b12.id, 'text' : 'branch123'})
  except tree.TreeException:
    print("Error: TreeException has occured")
  """

def getList_subbsOf(branch):
  """ getList of subbranches of "branch" in format for jstree """
  def getDict(branch):
    dict = {}
    dict['id'] = branch.id
    dict['text'] = branch.caption
    if branch.get_subbs() != [] :
      dict['state'] = {}
      dict['state']['opened'] = branch.folded ^ True
      if dict['state']['opened'] == True:
        dict['children'] = []
        for cur_subb in branch.get_subbs():
          dict['children'].append(getDict(cur_subb))
      else:
        dict['children'] = True
    return dict

  list = []
  if branch.get_subbs() != [] :
    for cur_subb in branch.get_subbs():
      list.append(getDict(cur_subb))
  return list


import cgi
#for_test()

form = cgi.FieldStorage()
cmd = form.getvalue('cmd', "")
id = form.getvalue('id', general.rootB_id)

print("Content-Type: text/html\n")
if cmd != "" :
  with Tree(treename) as curtree:
    if cmd == "load_subbs":
      print(json.dumps(getList_subbsOf(curtree.getB(id))))
    if cmd == "load_data":
      print(curtree.getB(id).text)
    if cmd == "save_data":
      data = form.getvalue('data', "")
      curtree.getB(id).text = data
    if cmd == "create_node":
      parent_id = form.getvalue('parent_id', general.rootB_id)
      parentB = curtree.getB(parent_id)
      newB = Branch()
      parentB.add_subb(newB)
      curtree.add(parentB)
      print(str( newB.id ))
    if cmd == "delete_node":
      branch = curtree.getB(id)
      curtree.remove(branch)
    if cmd == "rename_node":
      caption = form.getvalue('caption', "")
      curtree.getB(id).caption = caption
    if cmd == "move_node":
      new_parent_id = form.getvalue('new_parent', general.rootB_id)
      curtree.getB(id).parent_id = new_parent_id
