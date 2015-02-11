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
    b1 = Branch(tree=curtree, text="branch1", parent=rootb)
    b2 = Branch(tree=curtree, text="branch2", main=True, parent=rootb)
    b3 = Branch(tree=curtree, text="branch3", main=True, parent=rootb)
    b11 = Branch(tree=curtree, text="branch11", parent=b1)
    b12 = Branch(tree=curtree, text="branch12", parent=b1)

    # moving
    b21 = Branch(tree=curtree, text="branch21", main=True)
    curtree.moveB(b2, b21.id)

    b22 = Branch(tree=curtree, text="branch22")
    b23 = Branch(tree=curtree, text="branch23")
    curtree.moveB(b22, parent_id = b2.id)
    curtree.moveB(b23, parent_id = b2.id)

def getList_subbsOf(branch = general.rootB_id, nestedocs_mode = False):
  """
  getList of subbranches of "branch" in format for jstree
  nestedocs_mode:
    == True   --output not main branches only
    == False  --output main branches only
  """
  def getDict(branch = general.rootB_id):
    if nestedocs_mode :
      if branch.main:
        return None
    else:
      if not branch.main :
        return None

    dict = {}
    dict['id'] = branch.id
    dict['text'] = branch.text

    if branch.get_subbs() != [] :
      dict['state'] = {}
      dict['state']['opened'] = branch.folded ^ True
      if dict['state']['opened'] == True:
        dict['children'] = []
        for cur_subb in branch.get_subbs():
          newchild = getDict(branch = cur_subb)
          if newchild :
            dict['children'].append(newchild)
      else:
        dict['children'] = True
    return dict

  list = []
  subbs = branch.get_subbs()
  if len(subbs):
    for cur_subb in subbs:
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
id = 4
"""

print("Content-Type: text/html\n")
if cmd != "" :
  with Tree(treename) as curtree:
    if cmd == "fold":
      b = curtree.getB(id)
      b.folded = True
    elif cmd == "unfold":
      b = curtree.getB(id)
      b.folded = False
    elif cmd == "rename_node":
      text = form.getvalue('text', "")
      curtree.getB(id).text = text
    else:
      nestedocs = ( True if form.getvalue('nestedocs', 'False') == 'True' else False)
      if not nestedocs :
        if cmd == "load_subbs":
          print(json.dumps(getList_subbsOf(curtree.getB(id), nestedocs)))
        if cmd == "load_data":
          print(curtree.getB(id).text)
        if cmd == "create_node":
          parent_id = form.getvalue('parent_id', general.rootB_id)
          parentB = curtree.getB(parent_id)
          newB = Branch(tree = curtree, main = True, parent_id = parent_id)
          print(str( newB.id ))
        if cmd == "delete_node":
          branch = curtree.getB(id)
          curtree.remove(branch)
        if cmd == "move_node":
          b = curtree.getB(id)
          new_parent_id = form.getvalue('new_parent', general.rootB_id)
          position = int(form.getvalue('position', -1))
          curtree.moveB(b, new_parent_id, position)
      else:
        if cmd == "load_subbs":
          print(json.dumps(getList_subbsOf(curtree.getB(id), nestedocs)))
        if cmd == "load_data":
          print(curtree.getB(id).text)
        if cmd == "save_data":
          data = form.getvalue('data', "")
          curtree.getB(id).text = data
        if cmd == "create_node":
          parent_id = form.getvalue('parent_id', general.rootB_id)
          parentB = curtree.getB(parent_id)
          newB = Branch(tree = curtree, main = False, parent_id = parent_id)
          print(str( newB.id ))
        if cmd == "delete_node":
          branch = curtree.getB(id)
          curtree.remove(branch)
        if cmd == "move_node":
          b = curtree.getB(id)
          new_parent_id = form.getvalue('new_parent', general.rootB_id)
          position = int(form.getvalue('position', -1))
          curtree.moveB(b, new_parent_id, position)