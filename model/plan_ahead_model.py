# models/plan_model.py

plans = [
    {
        "id": 1,
        "type": "one-day",
        "date": "2025-11-15",
        "occasion": "Office",
        "location": "Delhi",
        "outfit": ["👔 Shirt", "👖 Formal Pants", "👞 Shoes"]
    },
    {
        "id": 2,
        "type": "trip",
        "start_date": "2025-12-01",
        "end_date": "2025-12-05",
        "occasion": ["Casual", "Party"],
        "location": "Goa",
        "outfits": [
            ["🩳 Shorts", "👕 T-shirt", "🕶 Sunglasses"],
            ["👕 Hawaiian Shirt", "👖 Jeans"]
        ]
    }
]


def get_all_plans():
    """Return all planned events."""
    return plans


def add_plan(plan):
    """Add a new plan."""
    plan["id"] = len(plans) + 1
    plans.append(plan)
    return plan
