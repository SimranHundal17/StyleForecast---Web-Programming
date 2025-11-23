# model/wardrobe_model.py

wardrobe_items = [
    {
        "id": 1,
        "name": "Blue Denim Shirt",
        "category": "Casual",
        "color": "Blue",
        "status": "Clean",
        "wear_count": 1,
        "icon": "👕"
    },
    {
        "id": 2,
        "name": "Black Jeans",
        "category": "Casual",
        "color": "Black",
        "status": "Clean",
        "wear_count": 2,
        "icon": "👖"
    },
    {
        "id": 3,
        "name": "White Formal Shirt",
        "category": "Formal",
        "color": "White",
        "status": "Needs Wash",
        "wear_count": 3,
        "icon": "👔"
    },
    {
        "id": 4,
        "name": "Leather Jacket",
        "category": "Party",
        "color": "Brown",
        "status": "Clean",
        "wear_count": 1,
        "icon": "🧥"
    },
    {
        "id": 5,
        "name": "Running Shoes",
        "category": "Gym",
        "color": "White",
        "status": "Clean",
        "wear_count": 5,
        "icon": "👟"
    },
    {
        "id": 6,
        "name": "Hiking Boots",
        "category": "Outdoor",
        "color": "Brown",
        "status": "Clean",
        "wear_count": 2,
        "icon": "🥾"
    },
    {
        "id": 7,
        "name": "Soccer Jersey",
        "category": "Sports",
        "color": "Red",
        "status": "Clean",
        "wear_count": 3,
        "icon": "🏃"
    },
]

# Safe ID counter
_next_id = max([item["id"] for item in wardrobe_items], default=0) + 1


def get_all_items():
    """Return all wardrobe items."""
    return wardrobe_items


def get_items_by_filter(filter_value):
    """
    Filter items based on filter value.
    - 'all': return all items
    - 'Needs Wash' or 'needs wash': return items that need washing
    - Other values: filter by category (case-insensitive)
    """
    if not filter_value or filter_value.lower() == 'all':
        return wardrobe_items.copy()
    
    filter_lower = filter_value.lower()
    
    # Special case: filter by status
    if filter_lower in ['needs wash', 'needs', 'needswash']:
        return [i for i in wardrobe_items if i["status"].lower() == "needs wash"]
    
    # Filter by category (case-insensitive)
    return [i for i in wardrobe_items if i["category"].lower() == filter_lower]


def get_items_by_status(status):
    """Return items with given status (Clean or Needs Wash)."""
    return [i for i in wardrobe_items if i["status"].lower() == status.lower()]


def get_item_by_id(item_id):
    """Get a single item by ID."""
    for item in wardrobe_items:
        if item["id"] == item_id:
            return item
    return None


def add_item(name, category, status, color=""):
    """Add new clothing item with safe ID generation."""
    global _next_id
    
    # Default icons by category
    default_icons = {
        "casual": "👕",
        "formal": "👔",
        "sports": "🏃",
        "gym": "🏋️",
        "party": "🎉",
        "outdoor": "🥾"
    }
    
    icon = default_icons.get(category.lower(), "👚")
    
    new_item = {
        "id": _next_id,
        "name": name,
        "category": category,
        "color": color,
        "status": status,
        "wear_count": 0,
        "icon": icon
    }
    
    wardrobe_items.append(new_item)
    _next_id += 1
    
    return new_item


def update_item_status(item_id):
    """Toggle item status between Clean and Needs Wash."""
    item = get_item_by_id(item_id)
    
    if not item:
        return None
    
    # Toggle status
    if item["status"].lower() == "clean":
        item["status"] = "Needs Wash"
        item["wear_count"] = item.get("wear_count", 0) + 1
    else:
        item["status"] = "Clean"
    
    return item


def delete_item(item_id):
    """Delete an item by ID."""
    global wardrobe_items
    wardrobe_items = [i for i in wardrobe_items if i["id"] != item_id]
    return True