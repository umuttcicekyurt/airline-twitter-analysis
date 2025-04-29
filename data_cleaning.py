'''
Cleaning:
-
-if important fields are null or cut off then discard (text, the username)
-removing duplicates(no same id)
-removing bots:
--if the time of creation of account is close to the time of the tweet
--no followers/friends
--low num of followers but a lot of tweets
--large following but little likes
-removing non-english tweets
-reject truncated tweets
'''
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["Twitter_analysis"]

collection = db["tweets"]

result = collection.insert_one({"text": "hello world", "likes": 0})

print(f"Inserted document ID: {result.inserted_id}")
