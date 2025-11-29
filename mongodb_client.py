from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def get_matches(user_id):
    doc = db.matches.find_one({"user_id": user_id})
    return doc["results"] if doc else None

def get_resume(user_id):
    return db.resumes.find_one({"user_id": user_id})
