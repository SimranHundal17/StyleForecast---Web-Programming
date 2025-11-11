# "Database" in memory — a list of dictionaries with clothing items
WARDROBE = [
    {
        "id": 1,
        "name": "Blue Shirt",
        "category": "Casual",
        "status": "Clean",
    },
    {
        "id": 2,
        "name": "Black Jeans",
        "category": "Casual",
        "status": "Needs Wash",
    },
]


def get_all_items():
    """
    Return all items from the wardrobe.
        This function is used by the /wardrobe route
        to send the item list into the wardrobe.html template.
    """
    return WARDROBE


def add_item(name, category, status):
    """
    Add a new item to the wardrobe.
        name      — item name (string)
        category  — category (Casual, Formal, Gym, etc.)
        status    — state (Clean / Needs Wash)
        For now everything is stored only in memory, no real DB.
    """

    if not name:
        return

    # Build a new dictionary with item data
    new_item = {
        "id": len(WARDROBE) + 1,   # RU: простой авто-инкремент ID / EN: simple auto-increment ID
        "name": name,
        "category": category or "Other",
        "status": status or "Clean",
    }

    # Append the new item to the list
    WARDROBE.append(new_item)
