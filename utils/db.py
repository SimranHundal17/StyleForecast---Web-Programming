from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DATABASE_NAME", "styleforecast")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("✅ Connected to MongoDB:", DB_NAME)
