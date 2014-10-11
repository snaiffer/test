#!/usr/bin/env python3.3

from flask import Flask
app = Flask(__name__)

@app.route('/abc/')
def hello_world():
  return 'Hello World!'

from flask import render_template

from branch import *
@app.route('/TreeMind/')
@app.route('/TreeMind/<path:path>')
def hello(path=None):
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

  """ """

  try:
    branch = getBranch_byURL(root, path)
    return render_template('show_branch.html', path=path, branch=branch.text)
  except notExist:
    return 'Branch isn\'t exist!'

if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0')
