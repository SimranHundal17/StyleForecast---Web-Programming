from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DATABASE_NAME", "styleforecast")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI missing in .env")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set. Check your .env file.")

print("✅ Connected to MongoDB:", DB_NAME)
