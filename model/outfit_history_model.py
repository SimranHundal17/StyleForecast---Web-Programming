# models/outfit_history_model.py
from utils.db import db

# Mongo collection
history_col = db["outfit_history"]


def _to_dict(doc):
    """Normalize MongoDB document to plain dict."""
    if not doc:
        return None

    return {
        "id": doc.get("id"),
        "date": doc.get("date", ""),
        "location": doc.get("location", ""),
        "weather": doc.get("weather", ""),
        "outfit": doc.get("outfit", []),
        "occasion": doc.get("occasion", ""),
        "mood": doc.get("mood", ""),
        "rating": doc.get("rating", 0),
        "liked": doc.get("liked", False),
    }


def _get_next_id():
    """Generate numeric ID like in wardrobe."""
    last = history_col.find_one(sort=[("id", -1)])
    if last:
        return int(last["id"]) + 1
    return 1


def get_all_history():
    """Fetch all history entries sorted by newest first."""
    docs = history_col.find().sort("id", -1)
    return [_to_dict(d) for d in docs]


def add_history_entry(entry):
    """Insert new entry into MongoDB."""
    new_id = _get_next_id()

    doc = {
        "id": new_id,
        "date": entry.get("date"),
        "location": entry.get("location"),
        "weather": entry.get("weather"),
        "outfit": entry.get("outfit", []),
        "occasion": entry.get("occasion", ""),
        "mood": entry.get("mood", ""),
        "rating": entry.get("rating", 0),
        "liked": entry.get("liked", False),
    }

    history_col.insert_one(doc)
    return _to_dict(doc)


def delete_history_entry(entry_id):
    """Delete entry by id."""
    res = history_col.delete_one({"id": int(entry_id)})
    return res.deleted_count > 0

