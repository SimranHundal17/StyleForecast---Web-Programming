from utils.db import db

users = db["users"]

def get_user_by_email(email):
    return users.find_one({"email": email})

def verify_user(email, password):
    return users.find_one({"email": email, "password": password})

def get_all_users():
    return list(users.find({}, {"password": 0}))

def get_current_user():
    return users.find_one({}, {"password": 0})

def update_user(email, data):
    users.update_one({"email": email}, {"$set": data})
    return get_user_by_email(data.get("email", email))

def create_user(data):
    if get_user_by_email(data["email"]):
        return None

    # Create ID field for compatibility
    last = users.find_one(sort=[("id", -1)])
    data["id"] = (last["id"] + 1) if last else 1

    users.insert_one(data)
    return data
