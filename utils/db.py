import os
from pymongo import MongoClient

# Read Mongo URL from environment variable (later we'll set it)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)

# Our database name
db = client["styleforecast"]

