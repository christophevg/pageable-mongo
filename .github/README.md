# Pageable Mongo

> Paging support for Mongo

[![Latest Version on PyPI](https://img.shields.io/pypi/v/pageable_mongo.svg)](https://pypi.python.org/pypi/pageable_mongo/)
[![Supported Implementations](https://img.shields.io/pypi/pyversions/pageable_mongo.svg)](https://pypi.python.org/pypi/pageable_mongo/)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.1.4-blue.svg)](https://github.com/christophevg/pypi-template)

## What is this?

This is merely a quick implementation and packaging of a way to use Mongo features to produce a Pageable-lookalike dictionary with information regarding the query that was performed. It is aimed at supporting applications that want to query in a pages way.

All credits go to [https://stackoverflow.com/a/53220591](https://stackoverflow.com/a/53220591), and even more to the Mongo developers ;-)

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


