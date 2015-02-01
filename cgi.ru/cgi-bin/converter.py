#!/usr/bin/env python3.2

import general
treename = general.testdb

from forest import Forest
from tree import Tree, Branch

from xml.etree.ElementTree import *

def exportFrom_basketNotes(treePath = "", treename = general.testdb):
  """
  Export the tree from BasKet Note Pads
  treePath  -- a path to the folder with BasKet hierarchy (with name "baskets")
    Ex.:
    treePath="/tmp/baskets/"
  treename  -- name of tree in which it'll be exported
  """
  try:
    with Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
  except ForestException:
    print("Error: ForestException has occured")

  with Tree(treename) as curtree:
    db_rootb = curtree.getB_root()

    def fillin_mainB(db_b, nodePath):
      nonlocal indent_level
      nodeXMLfile=".basket"
      nodeTree = ElementTree(file=(nodePath + nodeXMLfile))
      xml_rawroot = nodeTree.getroot()

      xml_root = xml_rawroot.getchildren()[1]

      def traverseBranch(xml_parent_b, db_parent_b, fillin_Parent = False):
        nonlocal indent_level
        for xml_b in xml_parent_b:
          if xml_b.tag == "note":
            type = xml_b.get("type")
            content = xml_b.find("content").text

            data = ""
            if type == "html":
              with open(nodePath + content) as nodeContFile:
                data = nodeContFile.read()
            elif type == "link" or type == "cross_reference" or type == "file" or type == "image":
              data = content
            else:
              data = content
              #print("\n Error: Unrecognized type of the note! \n")
            """
            elif type == "cross_reference":
            elif type == "file":
            elif type == "image":
              #<p><img alt="" data-cke-saved-src="www.ya.ru" src="www.ya.ru"><br></p>
            """
            if ( db_parent_b.text == "" and fillin_Parent ):
              print(indent(indent_level + 1) + str(content))
              db_parent_b.text = data
            else:
              print(indent(indent_level) + "subBranch: " + str(content))
              db_b = Branch(tree=curtree, main=False, folded=False, parent=db_parent_b)
              db_b.text = data
          if xml_b.tag == "group":
            # it is first level branches and has one groupe only
            if ( xml_root == xml_parent_b and len(xml_parent_b.getchildren()) == 1):
              traverseBranch(xml_b, db_parent_b, fillin_Parent = False)
            else:
              db_b = Branch(tree=curtree, main=False, folded=False, text="", parent=db_parent_b)
              #db_b = Branch(tree=curtree, main=False, folded=xml_b.get("folded"), text="", parent=db_parent_b)
              print(indent(indent_level) + "subBranch: ")
              indent_level += 1
              traverseBranch(xml_b, db_b, fillin_Parent = True)
              indent_level -= 1
      traverseBranch(xml_root, db_b)

    """
    temp_mainB = Branch(tree=curtree, caption="branch1", main=True, parent=db_rootb)
    nodePath="/tmp/basket6/"
    fillin_mainB(temp_mainB, nodePath)
    """

    treeXMLfile="baskets.xml"
    tree = ElementTree(file=(treePath + treeXMLfile))
    xml_root = tree.getroot()

    indent = (lambda indent_level = 1, indent_step = '  ': indent_level * indent_step)
    indent_level = 0
    def traverseTree(xml_parent_b, db_parent_b):
      nonlocal indent_level
      for xml_b in xml_parent_b:
        if xml_b.tag == "basket":
          b_name = xml_b.find("properties").find("name").text
          print(indent(indent_level) )
          print(indent(indent_level) + "Branch: " + str(b_name))
          db_b = Branch(tree=curtree, caption = b_name, text="", main=True, folded=False, parent=db_parent_b)
          #db_b = Branch(tree=curtree, main=True, folded=xml_b.get("folded"), text="", parent=db_parent_b)

          indent_level += 1
          fillin_mainB(db_b, treePath + xml_b.get("folderName"))
          traverseTree(xml_b, db_b)
          indent_level -= 1

    traverseTree(xml_root, db_rootb)

exportFrom_basketNotes("/export/")
