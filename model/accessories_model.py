# models/accessories_model.py

accessories = [
    {"id": 1, "name": "Leather Belt", "type": "Belt"},
    {"id": 2, "name": "Silver Earrings", "type": "Jewellery"},
    {"id": 3, "name": "Watch", "type": "Watch"},
    {"id": 4, "name": "Umbrella", "type": "Utility"},
    {"id": 5, "name": "Black Sunglasses", "type": "Sunglasses"},
]


def get_all_accessories():
    """Return all accessories."""
    return accessories


def add_accessory(name, type_):
    """Add a new accessory."""
    new = {"id": len(accessories) + 1, "name": name, "type": type_}
    accessories.append(new)
    return new


def remove_accessory(accessory_id):
    """Remove an accessory by ID."""
    global accessories
    accessories = [a for a in accessories if a["id"] != accessory_id]
