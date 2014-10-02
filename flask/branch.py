#!/usr/bin/env python3
"  "

import general
from copy import deepcopy

class Branch():
  "  "
  def __init__(self, text = "Unnamed", icon = 0, main = False, folded = False, type = 0, subBranches = [], data = [], usesNum = 0):
    """
    Name    DataType   Comment
    ------------------------------------------------------
    caption   string  first MAX_captionLen of <text>. For system use. 
    text      string  main text
    icon      int     id from the base of icons
    folded    bool    folded or unfolded
    main      bool    main branch is a branch which will be visiable at the left part. 
                      The main may became only that branch which parent is main.
    type      int     id from the base of types
    children  array   
    data      array   different files for "text" : media, archives etc
    usesNum   int     the number of uses current branch. 
                      Each click increments it.
    """
    self.text = text
    self.caption = self.create_caption()
    self.icon = icon
    self.main = main
    self.folded = folded
    self.type = type
    self.subBranches = deepcopy(subBranches)
    self.data = deepcopy(data)
    self.usesNum = usesNum

  def add_subBranch(self, subBranch):
    self.subBranches.append(subBranch)

  def getSubBranch_byCaption(self, caption):
    for subtree in self.subBranches:
      if subtree.caption == caption:
        return subtree
    raise notExist

  def __getitem__(self, index):
    try:
      return self.subBranches[index]
    except TypeError:
      pass
    return self.getSubBranch_byCaption(index)

  def __setitem__(self, index, value):
    self.subBranches.insert(index, value)

  def __len__(self):
    return len(self.subBranches)

  def create_caption(self):
    result = self.text
    if len(result) > general.MAX_captionLen :
      return result[0:general.MAX_captionLen] + "..."
    else :
      return result

  def __repr__(self):
    return self.__str__()
  def __str__(self):
    return self.caption

class notExist(Exception):
  pass

def getBranch(tree, caption):
  for subtree in tree.subBranches:
    if subtree.caption == caption:
      return subtree
    else:
      result = getBranch(subtree, caption)
      if result != None :
        return result

def getBranch_byURL(tree, url):
  if url == None:
    return tree
  path = url.split("/")
  curBranch = tree
  for branchCap in path:
    if branchCap != '':
      curBranch = curBranch[branchCap]
  return curBranch    

def print_all(branch, shift_toMainB = 0, shift_fromMainB = 0):
  if branch.folded :
    print("  " * shift_toMainB + "----------folded----------")
  else:
    for i in range(0, len(branch)):
      curBranch = branch[i]
      prev_shift_toMainB = shift_toMainB
      prev_shift_fromMainB = shift_fromMainB

      output = "  " * shift_toMainB
      if curBranch.main :
        output += "|- [" + str(curBranch.icon) + "] " 
        shift_toMainB += 1
        output += str(curBranch.caption)
      else:
        output += "-" + "-" * shift_fromMainB
        shift_fromMainB += 1
        output += str(curBranch.text)
      print(output)

      if len(curBranch) :
        print_all(curBranch, shift_toMainB, shift_fromMainB)

      shift_fromMainB = prev_shift_fromMainB
      shift_toMainB = prev_shift_toMainB

def getHtml_ofTree(root):

  def get_html_str_forbranch(branch, shift_toMainB = 0, shift_fromMainB = 0):
    nonlocal html_str
    if branch.folded :
      html_str += "<p>" + "  " * shift_toMainB + "----------folded----------" + "</p>\n"
    else:
      for i in range(0, len(branch)):
        html_str += "<p>"
        curBranch = branch[i]
        prev_shift_toMainB = shift_toMainB
        prev_shift_fromMainB = shift_fromMainB

        html_str += "  " * shift_toMainB
        if curBranch.main :
          html_str += "|- [" + str(curBranch.icon) + "] " 
          shift_toMainB += 1
          html_str += str(curBranch.caption)
        else:
          html_str += "-" + "-" * shift_fromMainB
          shift_fromMainB += 1
          html_str += str(curBranch.text)
        html_str += "</p>\n"

        if len(curBranch) :
          get_html_str_forbranch(curBranch, shift_toMainB, shift_fromMainB)

        shift_fromMainB = prev_shift_fromMainB
        shift_toMainB = prev_shift_toMainB

  html_str = ""
  get_html_str_forbranch(root)
  return html_str
          

if __name__ == '__main__':
  root = Branch(text = "root", main = True)

  branch0 = Branch(text = "Branch0", main = True)
  branch00 = Branch(text = "Branch00")
  branch000 = Branch(text = "Branch000")
  branch001 = Branch(text = "Branch001") #, folded = True)
  branch0010 = Branch(text = "Branch0010")
  branch01 = Branch(text = "Branch01")
  branch1 = Branch(text = "Branch1", main = True)
  root[0] = branch0
  root[0][0] = branch00
  root[0][0][0] = branch000
  root[0][0][1] = branch001
  root[0][0][1][0] = branch0010
  root[0][1] = branch01
  root[1] = branch1

  root.add_subBranch(Branch(
    text = "qwertyuiopasdfghjklzxcvbnm1234567890"))
  root.add_subBranch(Branch(
    text = "qwertyuiopasdfghjklzxcvbnm1234567890",
    main = True))

  print_all(root)

  print("")
  print(getHtml_ofTree(root))
  print("")
  print(root["Branch0"]["Branch00"]["Branch001"])
  print("\n getBranch :")
  print(getBranch(root, "Branch0010"))
  print("\n getBranch_byURL :")
  print(getBranch_byURL(root, "Branch0/Branch00/Branch001/Branch0010"))
  print(getBranch_byURL(root, "/Branch0/Branch01/"))
  print(getBranch_byURL(root, None))
  try:
    print(getBranch_byURL(root, "not/existed/branch"))
  except notExist:
    print("Error: The branch isn't exist!")
  


