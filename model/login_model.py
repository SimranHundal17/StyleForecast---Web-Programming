# models/user_model.py
users = [
    {
        "id": 1,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "1234",
        "style": "Casual",
        "climate": "Warm",
        "wash_after_wears": 3
    },
    {
        "id": 2,
        "name": "John Smith",
        "email": "john@example.com",
        "password": "abcd",
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
        return {k: v for k, v in user.items() if k != "password"}
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
