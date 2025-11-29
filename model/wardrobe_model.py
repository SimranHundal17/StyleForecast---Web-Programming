# model/wardrobe_model.py

from utils.db import db  # shared Mongo client / database

# use single collection for wardrobe items
wardrobe_col = db["wardrobe_items"]


def _to_dict(doc):   
    if not doc:
        return None

    return {
        "id": doc.get("id"),
        "name": doc.get("name", ""),
        "category": doc.get("category", ""),
        "color": doc.get("color", ""),
        "status": doc.get("status", "Clean"),
        "wear_count": doc.get("wear_count", 0),
        "icon": doc.get("icon", "👚"),
    }


def _get_next_id():
    last = wardrobe_col.find_one(sort=[("id", -1)])
    if last and "id" in last:
        return int(last["id"]) + 1
    return 1


def get_all_items():
    docs = wardrobe_col.find().sort("id", 1)
    return [_to_dict(d) for d in docs]


def get_items_by_filter(filter_value):
    if not filter_value or filter_value.lower() == "all":
        return get_all_items()

    filter_lower = filter_value.lower()

    # status filter "Needs Wash"
    if filter_lower in ["needs wash", "needs", "needswash"]:
        docs = wardrobe_col.find({"status": {"$regex": "^needs wash$", "$options": "i"}})
        return [_to_dict(d) for d in docs]

    # category filter (case-insensitive)
    docs = wardrobe_col.find(
        {"category": {"$regex": f"^{filter_lower}$", "$options": "i"}}
    )
    return [_to_dict(d) for d in docs]


def get_items_by_status(status):
    docs = wardrobe_col.find(
        {"status": {"$regex": f"^{status}$", "$options": "i"}}
    )
    return [_to_dict(d) for d in docs]


def get_item_by_id(item_id: int):
    doc = wardrobe_col.find_one({"id": int(item_id)})
    return _to_dict(doc)


def add_item(name: str, category: str, status: str, color: str = ""):
    # default icons by category
    default_icons = {
        "casual": "👕",
        "formal": "👔",
        "sports": "🏃",
        "gym": "🏋️",
        "party": "🎉",
        "outdoor": "🥾",
    }

    icon = default_icons.get(category.lower(), "👚")
    new_id = _get_next_id()

    doc = {
        "id": new_id,
        "name": name,
        "category": category,
        "color": color,
        "status": status,
        "wear_count": 0,
        "icon": icon,
    }

    # insert into Mongo
    wardrobe_col.insert_one(doc)

    # return normalized dict for JSON
    return _to_dict(doc)


def update_item_status(item_id: int):
    doc = wardrobe_col.find_one({"id": int(item_id)})
    if not doc:
        return None

    current_status = str(doc.get("status", "Clean")).lower()
    wear_count = int(doc.get("wear_count", 0))

    if current_status == "clean":
        new_status = "Needs Wash"
        wear_count += 1  # increase wear count when becoming dirty
    else:
        new_status = "Clean"

    wardrobe_col.update_one(
        {"id": int(item_id)},
        {"$set": {"status": new_status, "wear_count": wear_count}},
    )

    # read back updated doc
    updated = wardrobe_col.find_one({"id": int(item_id)})
    return _to_dict(updated)


def delete_item(item_id: int) -> bool:
    result = wardrobe_col.delete_one({"id": int(item_id)})
    return result.deleted_count > 0
