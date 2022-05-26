# Pageable Mongo

> Paging support for Mongo

[![Latest Version on PyPI](https://img.shields.io/pypi/v/pageable_mongo.svg)](https://pypi.python.org/pypi/pageable_mongo/)
[![Supported Implementations](https://img.shields.io/pypi/pyversions/pageable_mongo.svg)](https://pypi.python.org/pypi/pageable_mongo/)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.1.4-blue.svg)](https://github.com/christophevg/pypi-template)

## What is this?

This is merely a quick implementation and packaging of a way to use Mongo features to produce a Pageable-lookalike dictionary with information regarding the query that was performed. It is aimed at supporting applications that want to query in a pages way.

All credits go to [https://stackoverflow.com/a/53220591](https://stackoverflow.com/a/53220591), and even more to the Mongo developers ;-)

## Install

The usual `pip install pageable-mongo` will behave as expected and will also install PyMongo if not available, simply because without it, things will go wrond ;-)

```console
% pip install pageable-mongo          
Collecting pageable-mongo
  Using cached pageable_mongo-0.0.1-py3-none-any.whl (4.2 kB)
Collecting pymongo>=3.6
  Using cached pymongo-4.1.1-cp38-cp38-macosx_12_0_arm64.whl
Installing collected packages: pymongo, pageable-mongo
Successfully installed pageable-mongo-0.0.1 pymongo-4.1.1
```

## Minimal Survival Commands

```pycon
>>> import random
>>> import json
>>> 
>>> from pymongo import MongoClient
>>> from pageable_mongo import Pageable
>>> 
>>> mongo = MongoClient()
>>> db    = mongo["test"]
>>> 
>>> # generate some documents
>>> db["collection"].drop()
>>> values = [ "value 1", "value 2", "value 3", "value 4" ]
>>> for _ in range(10000):
...   result =db["collection"].insert_one({ "key" : random.choice(values) })
... 
>>> def query(db):
...   return db["collection"].find(
...     { "key" : { "$in" : [ "value 1", "value 4" ] } },
...     { "_id" : False }
...   ).sort("key", -1).skip(15).limit(10)
... 
>>> # classic query
>>> rows = query(db)
>>> print(json.dumps(list(rows), indent=2))
[
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  },
  {
    "key": "value 4"
  }
]
>>> # paged query
>>> pageable = query(Pageable(db))
>>> print(json.dumps(pageable.query,  indent=2))
[
  {
    "$match": {
      "key": {
        "$in": [
          "value 1",
          "value 4"
        ]
      }
    }
  },
  {
    "$facet": {
      "resultset": [
        {
          "$project": {
            "_id": false
          }
        },
        {
          "$sort": {
            "key": -1
          }
        },
        {
          "$skip": 15
        },
        {
          "$limit": 10
        }
      ],
      "total": [
        {
          "$count": "count"
        }
      ]
    }
  },
  {
    "$project": {
      "resultset": "$resultset",
      "total": {
        "$arrayElemAt": [
          "$total",
          0
        ]
      }
    }
  },
  {
    "$project": {
      "content": "$resultset",
      "totalElements": "$total.count"
    }
  }
]
>>> print(json.dumps(pageable.result, indent=2))
{
  "content": [
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    },
    {
      "key": "value 4"
    }
  ],
  "totalElements": 4906,
  "pageable": {
    "sort": {
      "sorted": true,
      "unsorted": false,
      "empty": false
    },
    "offset": 15,
    "pageNumber": 1,
    "pageSize": 10,
    "paged": true,
    "unpaged": false
  },
  "first": false,
  "last": false,
  "totalPages": 491,
  "numberOfElements": 10,
  "number": 15,
  "size": 10,
  "empty": false,
  "sort": {
    "sorted": true,
    "unsorted": false,
    "empty": false
  }
}
```

This example is also included in the repository:

```console
% python demo.py
```

## Exposing Collections via (Flask-)Restful API

Throwing Flask-Restful in the mix, a collection can be exposed like so:

```python
mongo = MongoClient()
db    = Pageable(mongo["test"])

class Collection(Resource):
  def get(self):
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
    db["collection"].limit(int(request.args.get("limit", 0)))

    return db.result

api.add_resource( Collection, "/api" )
```

To test just pass `property=value` pairs and optionally include `limit=<int>`, `start=<int>`, `sort=<property>` and `order=desc`

```console
% curl "http://localhost:8000/api?value=value_1&limit=3&start=2&sort=key&order=desc"
{
  "content": [
    {
      "key": "key_4",
      "value": "value_1"
    },
    {
      "key": "key_4",
      "value": "value_1"
    },
    {
      "key": "key_4",
      "value": "value_1"
    }
  ],
  "totalElements": 2555,
  "pageable": {
    "sort": {
      "sorted": true,
      "unsorted": false,
      "empty": false
    },
    "offset": 2,
    "pageNumber": 0,
    "pageSize": 3,
    "paged": true,
    "unpaged": false
  },
  "first": true,
  "last": false,
  "totalPages": 852,
  "numberOfElements": 3,
  "number": 2,
  "size": 3,
  "empty": false,
  "sort": {
    "sorted": true,
    "unsorted": false,
    "empty": false
  }
}
```

This example is also included in the repository:

```console
% pip install flask_restful gunicorn
% gunicorn api:app
[2022-05-26 17:41:40 +0200] [31123] [INFO] Starting gunicorn 20.1.0
[2022-05-26 17:41:40 +0200] [31123] [INFO] Listening at: http://127.0.0.1:8000 (31123)
[2022-05-26 17:41:40 +0200] [31123] [INFO] Using worker: sync
[2022-05-26 17:41:40 +0200] [31140] [INFO] Booting worker with pid: 31140
[2022-05-26 17:41:40 +0200] [api] [INFO] dropping 'collection'
[2022-05-26 17:41:40 +0200] [api] [INFO] generating 10000 documents in 'collection'
[2022-05-26 17:41:42 +0200] [api] [INFO] ready to answer queries...
```
