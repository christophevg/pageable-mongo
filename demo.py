import random
import json

from pymongo import MongoClient
from pageable_mongo import Pageable

mongo = MongoClient()
db    = mongo["test"]

# generate some documents
db["collection"].drop()
values = [ "value 1", "value 2", "value 3", "value 4" ]
for _ in range(10000):
  result =db["collection"].insert_one({ "key" : random.choice(values) })

def query(db):
  return db["collection"].find(
    { "key" : { "$in" : [ "value 1", "value 4" ] } },
    { "_id" : False }
  ).sort("key", -1).skip(15).limit(10)

# classic query
rows = query(db)
print(json.dumps(list(rows), indent=2))

# paged query
pageable = query(Pageable(db))
print(json.dumps(pageable.query,  indent=2))
print(json.dumps(pageable.result, indent=2))
