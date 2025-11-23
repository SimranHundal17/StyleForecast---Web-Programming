# models/user_model.py
users = [
    {
        "id": 1,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "123456",
        "style": "Casual",
        "climate": "Warm",
        "wash_after_wears": 3
    },
    {
        "id": 2,
        "name": "John Smith",
        "email": "john@example.com",
        "password": "123456",
        "style": "Formal",
        "climate": "Moderate",
        "wash_after_wears": 2
    }
]

def get_user_by_email(email):
    """Retrieve user by email."""
    for user in users:
        if user["email"] == email:
            return user
    return None


def verify_user(email, password):
    """Verify email/password combination."""
    user = get_user_by_email(email)
    if user and user["password"] == password:
        return user
    return None


def get_all_users():
    """Return list of all users (without passwords)."""
    return [{k: v for k, v in u.items() if k != "password"} for u in users]

def get_current_user():
    """Temporary: return the first user (pretend logged-in)."""
    user = users[0]
    return {k: v for k, v in user.items() if k != "password"}


def update_user(email, data):
    """Update a user's data fields (for profile form)."""
    for user in users:
        if user["email"] == email:
            for key, value in data.items():
                if key in user and key != "password":
                    user[key] = value
            return {k: v for k, v in user.items() if k != "password"}
    return None

def find_user_by_email(email: str):
    """Return user dict by email or None if not found."""
    email = (email or "").strip().lower()
    for user in get_all_users():
        if user.get("email", "").lower() == email:
            return user
    return None

def create_user(email: str, password: str, name: str | None = None):
    """
    Create a new user and return it.    
    """
    global users

    email = (email or "").strip()
    password = (password or "").strip()
    name = (name or "").strip() or email.split("@")[0]

    if not email or not password:
        raise ValueError("Email and password are required")

    # check duplicates
    if find_user_by_email(email) is not None:
        raise ValueError("User with this email already exists")

    # simple incremental id
    new_id = max((u.get("id", 0) for u in users), default=0) + 1

    new_user = {
      "id": new_id,
      "email": email,
      "password": password,
      "name": name,
    }

    users.append(new_user)
    return new_user