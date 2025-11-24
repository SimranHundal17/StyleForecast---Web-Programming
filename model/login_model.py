from utils.db import db

users = db["users"]

def get_user_by_email(email):
    return users.find_one({"email": email})

def get_all_users():
    return list(users.find({}, {"password": 0}))

def verify_user(email, password):
    return users.find_one({"email": email, "password": password})

def create_user(data):
    # Auto-increment id
    last = users.find_one(sort=[("id", -1)])
    data["id"] = (last["id"] + 1) if last else 1

    users.insert_one(data)
    return data
