# model/wardrobe_model.py
from datetime import datetime
from utils.db import db, laundry_db  # main DB and laundry DB

# Main collection where all wardrobe items are stored
wardrobe_col = db["wardrobe_items"]

# Separate collection for items that need wash
dirty_col = laundry_db["dirty_items"]

# Convert MongoDB document to a clean Python dict
## This avoids sending Mongo-specific fields to the frontend
def _to_dict(doc):
    if not doc:
        return None
    # Use safe defaults if some fields are missing
    return {
        "id": doc.get("id"),
        "name": doc.get("name", ""),
        "category": doc.get("category", ""),
        "color": doc.get("color", ""),
        "status": doc.get("status", "Clean"),
        "wear_count": doc.get("wear_count", 0),
        "icon": doc.get("icon", "👚"),
    }

# Generate a numeric ID similar to SQL auto-increment
def _get_next_id():
    last = wardrobe_col.find_one(sort=[("id", -1)])
    if last and "id" in last:
        return int(last["id"]) + 1
    return 1

# Return all wardrobe items, sorted by ID
def get_all_items():
    docs = wardrobe_col.find().sort("id", 1)
    return [_to_dict(d) for d in docs]

 # Filter items by status or category
 ## We filter by the 'status' field in the main collection
def get_items_by_filter(filter_value):
    if not filter_value or filter_value.lower() == "all":
        return get_all_items()

    filter_lower = filter_value.lower()

# Special handling for "Needs Wash" status
    if filter_lower in ["needs wash", "needs", "needswash"]:
        docs = wardrobe_col.find(
            {"status": {"$regex": "^needs wash$", "$options": "i"}}
        )
        return [_to_dict(d) for d in docs]

# Category filter (case-insensitive exact match)
    docs = wardrobe_col.find(
        {"category": {"$regex": f"^{filter_lower}$", "$options": "i"}}
# Regex allows us to avoid manual lower()/upper() logic. 
    )
    return [_to_dict(d) for d in docs]

# Get items by status using case-insensitive regex match
def get_items_by_status(status):
    docs = wardrobe_col.find(
        {"status": {"$regex": f"^{status}$", "$options": "i"}}
    )
    return [_to_dict(d) for d in docs]

# Find item by numeric id
def get_item_by_id(item_id: int):
    doc = wardrobe_col.find_one({"id": int(item_id)})
    return _to_dict(doc)

# Add a new wardrobe item
## If item is created as 'Needs Wash', also store it in dirty_items collection.
def add_item(name: str, category: str, status: str, color: str = ""):
    default_icons = {
        "casual": "👕",
        "formal": "👔",
        "sports": "🏃",
        "gym": "🏋️",
        "party": "🎉",
        "outdoor": "🥾",
    }
# Pick icon based on category (fallback icon if no match)
    icon = default_icons.get(category.lower(), "👚")
    new_id = _get_next_id()
# Build new item document
    doc = {
        "id": new_id,
        "name": name,
        "category": category,
        "color": color,
        "status": status,
        "wear_count": 0,
        "icon": icon,
    }

# Insert into main wardrobe collection
    wardrobe_col.insert_one(doc)

# If item is created as "Needs Wash" -> add to dirty collection
    if str(status).lower() == "needs wash":
        dirty_col.update_one(
            {"item_id": new_id},
            {
                "$set": {
                    "item_id": new_id,
                    "marked_at": datetime.utcnow(),
                }
            },
            upsert=True,   # create new doc if it does not exist
        )

    return _to_dict(doc)

# Update item status between 'Clean' and 'Needs Wash'
## Also keep dirty_items collection in sync
def update_item_status(item_id: int):
# Find item in main collection
    doc = wardrobe_col.find_one({"id": int(item_id)})
    if not doc:
        return None
# Normalize current status to lower-case string
    current_status = str(doc.get("status", "Clean")).lower()
    wear_count = int(doc.get("wear_count", 0))

    if current_status == "clean":
# Mark item as dirty
        new_status = "Needs Wash"
        wear_count += 1  # increase wear count when becoming dirty

# Add or update record in dirty_items
        dirty_col.update_one(
            {"item_id": int(item_id)},
            {
                "$set": {
                    "item_id": int(item_id),
                    "marked_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
    else:
# Mark item as clean
        new_status = "Clean"

# Remove item from dirty_items when it becomes clean
        dirty_col.delete_one({"item_id": int(item_id)})

# Update status and wear_count in main wardrobe collection
    wardrobe_col.update_one(
        {"id": int(item_id)},
        {"$set": {"status": new_status, "wear_count": wear_count}},
    )

# Read back updated document to return fresh data
    updated = wardrobe_col.find_one({"id": int(item_id)})
    return _to_dict(updated)

# Delete item from wardrobe (and dirty_items if applicable)
def delete_item(item_id: int) -> bool:
# Remove item from main collection
    result = wardrobe_col.delete_one({"id": int(item_id)})
# Also clean up from dirty_items (if it was marked as dirty)
    dirty_col.delete_one({"item_id": int(item_id)})
# Return True if something was actually deleted
    return result.deleted_count > 0
