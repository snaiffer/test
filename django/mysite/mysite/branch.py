#!/usr/bin/env python
"  "

import general
from copy import deepcopy

class Branch():
  "  "
  def __init__(self, text = "Unnamed", icon = 0, main = False, folded = False, type = 0, subBranches = [], data = [], usesNum = 0):
    """
    Name    DataType   Comment
    ------------------------------------------------------
    text      string  html doc
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
    self.icon = icon
    self.main = main
    self.folded = folded
    self.type = type
    self.subBranches = deepcopy(subBranches)
    self.data = deepcopy(data)
    self.usesNum = usesNum

  def add_subBranch(self, subBranch):
    self.subBranches.append(subBranch)

  def __getitem__(self, index):
    return self.subBranches[index]

  def __setitem__(self, index, value):
    self.subBranches.insert(index, value)

  def __len__(self):
    return len(self.subBranches)

  def get_caption(self):
    result = self.text
    """
    remove html symbols
    """
    if len(result) > general.MAX_captionLen :
      return result[0:general.MAX_captionLen] + "..."
    else :
      return result

  def __repr__(self):
    return self.__str__()
  def __str__(self):
    return "[" + str(self.icon) + "] " + self.text

"""
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
        output += str(curBranch.get_caption())
      else:
        output += "-" + "-" * shift_fromMainB
        shift_fromMainB += 1
        output += str(curBranch.text)
      print(output)

      if len(curBranch) :
        print_all(curBranch, shift_toMainB, shift_fromMainB)

      shift_fromMainB = prev_shift_fromMainB
      shift_toMainB = prev_shift_toMainB
"""

html_str = ""

def getHtml_ofTree(root):

  def get_html_str_forbranch(branch, shift_toMainB = 0, shift_fromMainB = 0):
    global html_str
    
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
          html_str += str(curBranch.get_caption())
        else:
          html_str += "-" + "-" * shift_fromMainB
          shift_fromMainB += 1
          html_str += str(curBranch.text)
        html_str += "</p>\n"

        if len(curBranch) :
          get_html_str_forbranch(curBranch, shift_toMainB, shift_fromMainB)

        shift_fromMainB = prev_shift_fromMainB
        shift_toMainB = prev_shift_toMainB

  get_html_str_forbranch(root)
          

def test():
  root = Branch(text = "root", main = True)

  branch0 = Branch(text = "Branch0", main = True)
  branch00 = Branch(text = "Branch00")
  branch000 = Branch(text = "Branch000")
  branch001 = Branch(text = "Branch001", folded = True)
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

  getHtml_ofTree(root)
  return html_str


if __name__ == '__main__':
  print test() 
"""
  root = Branch(text = "root", main = True)

  branch0 = Branch(text = "Branch0", main = True)
  branch00 = Branch(text = "Branch00")
  branch000 = Branch(text = "Branch000")
  branch001 = Branch(text = "Branch001", folded = True)
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

  print("\n")
  print(getHtml_ofTree(root))

"""


