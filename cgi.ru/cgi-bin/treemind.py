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

def getList_subbsOf(branch = general.rootB_id, nestedocs_mode = False):
  """
  getList of subbranches of "branch" in format for jstree
  nestedocs_mode:   
    == True   --output text field of branches and output all branches
    == False  --output caption field of branches and output main branches only
  """
  def getDict(branch = general.rootB_id, hostb = True):
    if nestedocs_mode :
      if branch.main and not hostb:
        return None
      else:
        hostb = False
    else:
      if not branch.main :
        return None

    dict = {}
    dict['id'] = branch.id
    dict['text'] = branch.text if nestedocs_mode else branch.caption

    if branch.get_subbs() != [] :
      dict['state'] = {}
      dict['state']['opened'] = branch.folded ^ True
      if dict['state']['opened'] == True:
        dict['children'] = []
        for cur_subb in branch.get_subbs():
          newchild = getDict(branch = cur_subb, hostb = False)
          if newchild :
            dict['children'].append(newchild)
      else:
        dict['children'] = True
    return dict

  list = []
  if nestedocs_mode :
    newsubb = getDict(branch)
    if newsubb :
      list.append(newsubb)
  else :
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
id = 10
"""

print("Content-Type: text/html\n")
if cmd != "" :
  with Tree(treename) as curtree:
    if cmd == "load_subbs":
      nestedocs = ( True if form.getvalue('nestedocs', 'False') == 'True' else False)
      print(json.dumps(getList_subbsOf(curtree.getB(id), nestedocs)))
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
