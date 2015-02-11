#!/usr/bin/env python3.2

import general
treename = general.testdb

import general
from tree import *

import json

def for_test():
  Forest().remove()
  Users().removeAll()

  alex = Users("Alex", "123", "alex@gmail.com")
  bob = Users("Bob", "123456", "bob@gmail.com")

  testTree1 = Tree(alex, "testTree1")
  testTree2 = Tree(alex, "testTree2")
  testTree3 = Tree(bob, "testTree3")
  testTree4 = Tree(alex, "testTree4")

  for curT in Forest().allTrees():
    rootb = curT.rootb
    b1 = Branch(text="branch1_" + str(curT.name), parent=rootb)
    b11 = Branch(text="branch11_" + str(curT.name), parent=b1)
    b12 = Branch(text="branch12_" + str(curT.name), parent=b1)

    b2 = Branch(text="branch2_" + str(curT.name), main=True, parent=rootb)
    b21 = Branch(text="branch21_" + str(curT.name), parent=b2)

    b3 = Branch(text="branch3_" + str(curT.name), main=True, parent=rootb)
    b31 = Branch(text="branch31_" + str(curT.name), parent=b3)

def getList_subbsOf(branch, nestedocs_mode = False):
  """
  getList of subbranches of "branch" in format for jstree
  nestedocs_mode:
    == True   --output not main branches only
    == False  --output main branches only
  """
  def getDict(branch):
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
curuser = session.query(Users).filter_by(nickname='Bob').scalar()

form = cgi.FieldStorage()
curtree_id = form.getvalue('tree', curuser.get_latestTree().id)
curtree = curuser.getTree(curtree_id)
cmd = form.getvalue('cmd', "")
id = form.getvalue('id', curtree.rootb_id)
if id == '#':
  id = curtree.rootb_id

"""
cmd = "load_subbs"
id = 4
id = '#'
"""

print("Content-Type: text/html\n")
if cmd != "" :
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
        #curtree.set_latestB(id)
      if cmd == "load_data":
        print(curtree.getB(id).text)
      if cmd == "create_node":
        parent_id = form.getvalue('parent_id', curtree.rootb_id)
        parentB = curtree.getB(parent_id)
        newB = Branch(main = True, parent_id = parent_id)
        print(str( newB.id ))
      if cmd == "delete_node":
        branch = curtree.getB(id)
        branch.remove()
      if cmd == "move_node":
        b = curtree.getB(id)
        new_parent_id = form.getvalue('new_parent', curtree.rootb_id)
        position = int(form.getvalue('position', -1))
        b.move(new_parent_id, position)
    else:
      if cmd == "load_subbs":
        print(json.dumps(getList_subbsOf(curtree.getB(id), nestedocs)))
      if cmd == "load_data":
        print(curtree.getB(id).text)
      if cmd == "save_data":
        data = form.getvalue('data', "")
        curtree.getB(id).text = data
      if cmd == "create_node":
        parent_id = form.getvalue('parent_id', curtree.rootb_id)
        parentB = curtree.getB(parent_id)
        newB = Branch(main = False, parent_id = parent_id)
        print(str( newB.id ))
      if cmd == "delete_node":
        branch = curtree.getB(id)
        branch.remove()
      if cmd == "move_node":
        b = curtree.getB(id)
        new_parent_id = form.getvalue('new_parent', curtree.rootb_id)
        position = int(form.getvalue('position', -1))
        b.move(new_parent_id, position)
session.commit()
