import sys

sys.path.insert(
    1, "/Users/Learning/workspace/project_2/virtual/lib/python3.9/site-packages"
)

from decouple import config
import pymongo
from pymongo import MongoClient

API_CONNECTION = config("CONNECTION")

cluster = MongoClient(API_CONNECTION)
db = cluster["CS50"]
collection = db["users"]

post1 = {"_id": 5, "name": "joe"}
post2 = {"_id": 6, "name": "bill"}

rows = list(collection.find({"username": "tt"}))
print(rows)
print(rows[0]["userId"])

# print(list(results))
# for result in results:
#     print(result)


# post_count = collection.count_documents({})
# print(post_count)
