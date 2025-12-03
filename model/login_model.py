from utils.db import db
import bcrypt

users = db["users"]


def get_user_by_email(email: str):
    """Return user document by email."""
    return users.find_one({"email": email})


def get_all_users():
    """
    Return list of users without password field.    
    """
    return list(users.find({}, {"password": 0}))


def verify_user(email: str, password: str):
    """
    Verify user credentials with bcrypt.
    Returns user document if password is correct, otherwise None.
    """
    user = users.find_one({"email": email})
    if not user:
        return None

    stored_hash = user.get("password")
    if not stored_hash:
        return None

    # stored_hash is saved as string, so we convert it back to bytes
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    # bcrypt.checkpw expects bytes (raw_password, hashed_password)
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return user

    return None


def create_user(data: dict):
    """
    Create a new user with auto-increment id.
    Password is hashed with bcrypt before storing.
    """
    raw_password = data.get("password")

    if not raw_password:
        raise ValueError("Password is required for user creation")

    # Generate bcrypt hash (salt is included inside the hash)
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())

    # Store hash as utf-8 string in Mongo
    data["password"] = hashed.decode("utf-8")

    # Auto-increment numeric id
    last = users.find_one(sort=[("id", -1)])
    data["id"] = (last["id"] + 1) if last else 1

    users.insert_one(data)
    return data
