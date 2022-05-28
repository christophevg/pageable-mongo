from pageable_mongo import Pageable
import mongomock

def test_basic_query_generation():
  pageable = Pageable(mongomock.MongoClient().db)["collection"]
  pageable.find(
    { "key" : "value" },
    { "_id" : False }
  ).sort("key", -1).skip(5).limit(10)

  assert pageable.query == [
    { "$match":  { "key" : "value" }},
    { "$facet": {
      "resultset": [
        { "$project" : { "_id" : False } },
        { "$sort"    : { "key" : -1 } },
        { "$skip"    : 5 },
        { "$limit"   : 10 }
      ],
      "total": [
        { "$count": "count" }
      ]
    }},
    { "$project" : {
      "resultset" : "$resultset",
      "total"     : { "$arrayElemAt": [ "$total", 0] }
    }},
    { "$project" : {
      "content"       : "$resultset",
      "totalElements" : "$total.count"
    }}
  ]
