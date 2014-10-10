#!/usr/bin/env python3.3

treename = "treemind2" #

import general
import forest as f
import tree as t

from flask import Flask
app = Flask(__name__)
from flask import render_template

@app.route('/')
def main():
  return render_template('show_branch.html')
  """
  try:
    with t.Tree(treename) as tree:
  except t.TreeException:  
    print("Error: TreeException has occured")
  """

@app.route('/branches/id=<int:id>/<command>')
@app.route('/branches/id=<int:id>/<command>/text=<text>')
def treemind(id, command, text=None):
  try:
    with t.Tree(treename) as tree:
      if command == "get_text":
        return tree.get_text(id)
      if command == "update_text":
        tree.update_text(id, text)
        return tree.get_text(id)
  except t.TreeException:  
    print("Error: TreeException has occured")

def for_test():
  try:
    with f.Forest() as forest:
      forest.removeTree(treename)
      forest.plantTree(treename)
  except f.ForestException:
    print("Error: ForestException has occured")

  try:
    with t.Tree(treename) as tree:
      tree.insertB(general.rootB_id, 'branch1')
      tree.insertB(general.rootB_id, 'branch2')
      tree.insertB(2, 'branch11')
      tree.insertB(2, 'branch12')
  except t.TreeException:  
    print("Error: TreeException has occured")

if __name__ == '__main__':
  for_test()
  app.debug = True
  app.run(host='0.0.0.0')
