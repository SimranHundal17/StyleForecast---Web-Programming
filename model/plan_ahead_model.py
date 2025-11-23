from datetime import datetime, timedelta
from utils.db import db

plans = db["plans"]

# We keep counters because your app depends on id and group_id
# We initialize them by checking existing DB entries
def _get_next_id():
    last = plans.find_one(sort=[("id", -1)])
    return (last["id"] + 1) if last else 1

def _get_next_group_id():
    last = plans.find_one(sort=[("group_id", -1)])
    return (last["group_id"] + 1) if last else 1


# -------------------------
# GET ALL PLANS
# -------------------------
def get_all_plans():
    return list(plans.find())


# -------------------------
# GET PLANS FOR A DATE
# -------------------------
def get_plans_for_date(date_str):
    return list(plans.find({"date": date_str}))


# -------------------------
# GET PLAN BY ID
# -------------------------
def get_plan_by_id(pid):
    return plans.find_one({"id": int(pid)})


# -------------------------
# ADD SINGLE-DAY PLAN
# -------------------------
def add_plan_entry(entry):
    new_entry = dict(entry)
    new_entry["id"] = _get_next_id()

    # Defaults (keep matching your original model)
    new_entry.setdefault("location", "")
    new_entry.setdefault("lat", None)
    new_entry.setdefault("lon", None)
    new_entry.setdefault("occasion", "Casual")
    new_entry.setdefault("weather", "")
    new_entry.setdefault("outfit", [])
    new_entry.setdefault("liked", False)
    new_entry.setdefault("rating", None)
    new_entry.setdefault("group_id", None)

    plans.insert_one(new_entry)
    return new_entry


# -------------------------
# ADD RANGE OF DATES
# -------------------------
def add_plan_range(start_date_str, end_date_str, base_entry):
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    if end < start:
        start, end = end, start

    group = _get_next_group_id()
    created = []

    current = start
    while current <= end:
        e = dict(base_entry)
        e["date"] = current.strftime("%Y-%m-%d")
        new_entry = add_plan_entry(e)

        # Update its group_id
        plans.update_one({"id": new_entry["id"]}, {"$set": {"group_id": group}})
        new_entry["group_id"] = group

        created.append(new_entry)
        current += timedelta(days=1)

    return created


# -------------------------
# UPDATE PLAN FIELDS
# -------------------------
def update_plan(entry_id, **kwargs):
    plans.update_one({"id": int(entry_id)}, {"$set": kwargs})
    return get_plan_by_id(entry_id)


# -------------------------
# UPDATE RATING & LIKE
# -------------------------
def update_plan_rating(entry_id, rating=None, liked=None):
    update = {}
    if rating is not None:
        update["rating"] = rating
    if liked is not None:
        update["liked"] = bool(liked)

    plans.update_one({"id": int(entry_id)}, {"$set": update})
    return get_plan_by_id(entry_id)


# -------------------------
# DELETE SINGLE PLAN ENTRY
# -------------------------
def delete_plan(entry_id):
    plans.delete_one({"id": int(entry_id)})
    return True


# -------------------------
# DELETE GROUP OF PLANS
# -------------------------
def delete_group(group_id):
    plans.delete_many({"group_id": int(group_id)})
    return True
