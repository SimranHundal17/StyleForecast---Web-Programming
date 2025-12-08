from datetime import datetime, timedelta
from utils.db import db

plans = db["plans"]

def serialize_plan(p):
    if not p:
        return None

    return {
        "id": int(p.get("id")),
        "date": p.get("date"),
        "location": p.get("location"),
        "lat": p.get("lat"),
        "lon": p.get("lon"),
        "occasion": p.get("occasion"),
        "weather": p.get("weather"),
        "temp": p.get("temp"),
        "description": p.get("description"),
        "outfit": p.get("outfit", []),
        "group_id": int(p.get("group_id")) if p.get("group_id") is not None else None
    }

def _next_id():
    last = plans.find_one(sort=[("id", -1)])
    return (last["id"] + 1) if last else 1

def _next_group_id():
    last = plans.find_one(sort=[("group_id", -1)])
    return (last["group_id"] + 1) if last else 1

def get_all_plans():
    return list(plans.find())

def get_plans_for_date(date_str):
    return list(plans.find({"date": date_str}))

def get_plan_by_id(pid):
    return plans.find_one({"id": int(pid)})

def add_plan_entry(entry):
    new_entry = dict(entry)
    new_entry["id"] = _next_id()

    new_entry.setdefault("location", "")
    new_entry.setdefault("lat", None)
    new_entry.setdefault("lon", None)
    new_entry.setdefault("occasion", "Casual")
    new_entry.setdefault("weather", "")
    new_entry.setdefault("temp", None)
    new_entry.setdefault("description", None)
    new_entry.setdefault("outfit", [])
    new_entry.setdefault("group_id", None)

    plans.insert_one(new_entry)
    return new_entry

def add_plan_range(start_date, end_date, entry_template):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end < start:
        start, end = end, start

    gid = _next_group_id()
    created = []
    cur = start

    while cur <= end:
        entry = dict(entry_template)
        entry["date"] = cur.strftime("%Y-%m-%d")
        new_entry = add_plan_entry(entry)

        plans.update_one({"id": new_entry["id"]},
                         {"$set": {"group_id": gid}})

        new_entry["group_id"] = gid
        created.append(new_entry)
        cur += timedelta(days=1)

    return created

def update_plan(pid, **fields):
    plans.update_one({"id": int(pid)}, {"$set": fields})
    return get_plan_by_id(pid)

def delete_plan(pid):
    plans.delete_one({"id": int(pid)})
    return True

def delete_group(gid):
    plans.delete_many({"group_id": int(gid)})
    return True
