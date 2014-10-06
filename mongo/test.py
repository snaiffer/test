#!/usr/bin/env python3


import pymongo
import copy

con = pymongo.Connection(host="localhost")

db = con.test
treemind = db.treemind

treemind.insert({"caption":"branch0","text":"branch0_text"})
#treemind.insert({"date":"12.1991","rate":None})

for cur in treemind.find():
  print(str(cur['caption']) + str(cur['text']))


"""
for cur in result.find():
  curdate = {"date": cur['date'] }
  curid = {"_id": cur['_id']}
  #print(curdate)
  docWith_rate = indexes.find_one(curdate)
  rate = None
  if docWith_rate == None :
    rate = 3.171
  else:
    rate = docWith_rate['rate']
  print(rate)
  cur['rate'] = rate
  print(cur['date'])
  result.update(curid, cur, safe=True)


result.insert({"date":"12.1991","rate":None})
"""
