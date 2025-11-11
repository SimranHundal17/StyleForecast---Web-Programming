# models/wardrobe_model.py

wardrobe_items = [
    {"id": 1, "name": "Blue Denim Shirt", "category": "Shirt", "occasion": "Casual", "color": "Blue", "status": "Clean", "wear_count": 1},
    {"id": 2, "name": "Black Jeans", "category": "Pants", "occasion": "Casual", "color": "Black", "status": "Clean", "wear_count": 2},
    {"id": 3, "name": "White Formal Shirt", "category": "Shirt", "occasion": "Formal", "color": "White", "status": "Needs Wash", "wear_count": 3},
    {"id": 4, "name": "Leather Jacket", "category": "Jacket", "occasion": "Party", "color": "Brown", "status": "Clean", "wear_count": 1},
]


def get_all_items():
    """Return all wardrobe items."""
    return wardrobe_items


def get_items_by_status(status):
    """Return items with given status (Clean or Needs Wash)."""
    return [i for i in wardrobe_items if i["status"].lower() == status.lower()]


def add_item(item):
    """Add new clothing item."""
    item["id"] = len(wardrobe_items) + 1
    wardrobe_items.append(item)
    return item
