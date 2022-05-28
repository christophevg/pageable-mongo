import logging
logger = logging.getLogger(__name__)

LOG_LEVEL = "INFO"
FORMAT    = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"
logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)

from timeit import default_timer as timer
import random
import json

from pymongo import MongoClient
from pageable_mongo import Pageable

from flask import Flask, request
from flask_restful import Resource, Api

mongo = MongoClient()
db    = Pageable(mongo["test"])

DOCUMENTS = 10000

# generate some documents
logger.info("dropping 'collection'")
db["collection"].drop()
logger.info(f"generating {DOCUMENTS} documents in 'collection'")
keys   = [ "key_1", "key_2", "key_3", "key_4" ]
values = [ "value_1", "value_2", "value_3", "value_4" ]
for _ in range(DOCUMENTS):
  result = db["collection"].insert_one({
    "key"   : random.choice(keys),
    "value" : random.choice(values)
  })

app = Flask(__name__)
app.config["RESTFUL_JSON"]= { 'indent': 2 }
api = Api(app)

class Collection(Resource):
  def get(self):
    start = timer()
    # construct filters for arg=value as property filters
    # semantics: check if value is part of that property
    filters = {
      arg :  { "$regex" : value, "$options" : "i" }
      for arg, value in request.args.items()
      if not arg in [ "sort", "order", "start", "limit" ]
    }
    db["collection"].find(filters, { "_id": False })

    # add sorting
    sort = request.args.get("sort",  None)
    if sort:
      order =request.args.get("order", None)
      db["collection"].sort( sort, -1 if order == "desc" else 1)

    # add paging
    db["collection"].skip(int(request.args.get("start", 0)))
    result = db["collection"].limit(int(request.args.get("limit", 0)))

    answer = {
      "content"  : list(result),
      "pageable" : result.pageable
    }
    end = timer()
    logger.info(f"answered query in {(end - start)*1000:.04}ms")
    return answer

api.add_resource( Collection, "/api" )

logger.info("ready to answer queries...")
