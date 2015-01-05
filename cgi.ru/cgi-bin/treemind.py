#!/usr/bin/env python3.2

import general
treename = general.testdb

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
    b1 = Branch(tree=curtree, caption="branch1", parent=rootb)
    b2 = Branch(tree=curtree, caption="branch2", parent=rootb)
    b3 = Branch(tree=curtree, caption="branch3", parent=rootb)
    b11 = Branch(tree=curtree, caption="branch11", parent=b1)
    b12 = Branch(tree=curtree, caption="branch12", parent=b1)

    # moving
    b21 = Branch(tree=curtree, caption="branch21")
    curtree.moveB(b2, b21.id)

    b22 = Branch(tree=curtree, caption="branch22")
    b23 = Branch(tree=curtree, caption="branch23")
    curtree.moveB(b22, parent_id = b2.id)
    curtree.moveB(b23, parent_id = b2.id)

def getList_subbsOf(branch = general.rootB_id, main_only = False, caption_only = True):
  """
  getList of subbranches of "branch" in format for jstree
  main_only:
    if main_only == True then output main branches only
    if main_only == False then output NOT main branches only
  caption_only:
    if caption_only == True then output caption field
    if caption_only == False then output text field
  """
  def getDict(branch = general.rootB_id):
    if main_only :
      if not branch.main :
        return None
    else :
      if branch.main :
        return None
    dict = {}
    dict['id'] = branch.id
    if caption_only :
      dict['text'] = branch.caption
    else:
      dict['text'] = branch.text
    if branch.get_subbs() != [] :
      dict['state'] = {}
      dict['state']['opened'] = branch.folded ^ True
      if dict['state']['opened'] == True:
        dict['children'] = []
        for cur_subb in branch.get_subbs():
          newchild = getDict(cur_subb)
          if newchild :
            dict['children'].append(newchild)
      else:
        dict['children'] = True
    return dict

  list = []
  if branch.get_subbs() != [] :
    for cur_subb in branch.get_subbs():
      newsubb = getDict(cur_subb)
      if newsubb :
        list.append(newsubb)
  return list


import cgi
#for_test()

form = cgi.FieldStorage()
cmd = form.getvalue('cmd', "")
id = form.getvalue('id', general.rootB_id)

"""
cmd = "load_subbs"
id = 7
"""

print("Content-Type: text/html\n")
if cmd != "" :
  with Tree(treename) as curtree:
    if cmd == "load_subbs":
      main_only = ( True if form.getvalue('main_only', 'True') == 'True' else False)
      caption_only = ( True if form.getvalue('caption_only', 'True') == 'True' else False)
      print(json.dumps(getList_subbsOf(curtree.getB(id), main_only, caption_only)))
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
      b = curtree.getB(id)
      new_parent_id = form.getvalue('new_parent', general.rootB_id)
      position = int(form.getvalue('position', -1))
      curtree.moveB(b, new_parent_id, position)
