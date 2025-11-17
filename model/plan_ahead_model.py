# model/plan_ahead_model.py
from datetime import datetime, timedelta

# In-memory plans list. Each plan is a dict:
# { id, date (YYYY-MM-DD), location, lat, lon, occasion, weather, outfit, liked, rating, group_id }
plans = []
_next_id_counter = 1
_next_group_counter = 1

def _next_id():
    global _next_id_counter
    v = _next_id_counter
    _next_id_counter += 1
    return v

def _next_group_id():
    global _next_group_counter
    v = _next_group_counter
    _next_group_counter += 1
    return v

def get_all_plans():
    return plans.copy()

def get_plans_for_date(date_str):
    return [p for p in plans if p.get("date") == date_str]

def get_plan_by_id(pid):
    for p in plans:
        if p.get("id") == int(pid):
            return p
    return None

def add_plan_entry(entry):
    """
    entry: dict must contain 'date', 'location' (optional), 'lat','lon','occasion'
    Adds id + defaults.
    """
    e = dict(entry)
    e["id"] = _next_id()
    e.setdefault("location", "")
    e.setdefault("lat", None)
    e.setdefault("lon", None)
    e.setdefault("occasion", "Casual")
    e.setdefault("weather", "")
    e.setdefault("outfit", [])
    e.setdefault("liked", False)
    e.setdefault("rating", None)
    e.setdefault("group_id", None)  # group id for multi-day ranges
    plans.append(e)
    return e

def add_plan_range(start_date_str, end_date_str, base_entry):
    """
    Add one entry per date inclusive. base_entry is dict with location/lat/lon/occasion
    Returns list of created entries.
    """
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    if end < start:
        start, end = end, start
    group = _next_group_id()
    created = []
    current = start
    while current <= end:
        e = dict(base_entry)
        e["date"] = current.strftime("%Y-%m-%d")
        created_entry = add_plan_entry(e)
        created_entry["group_id"] = group
        created.append(created_entry)
        current += timedelta(days=1)
    return created

def update_plan(entry_id, **kwargs):
    """
    Update fields for a single plan. Allowed keys: location, lat, lon, occasion, weather, outfit, liked, rating
    Returns updated plan or None.
    """
    p = get_plan_by_id(entry_id)
    if not p:
        return None
    for k, v in kwargs.items():
        if k in p:
            p[k] = v
    return p

def update_plan_rating(entry_id, rating=None, liked=None):
    p = get_plan_by_id(entry_id)
    if not p:
        return None
    if rating is not None:
        p["rating"] = rating
    if liked is not None:
        p["liked"] = bool(liked)
    return p

def delete_plan(entry_id):
    global plans
    pid = int(entry_id)
    found = False
    for p in plans:
        if p.get("id") == pid:
            found = True
            break
    if not found:
        return False
    plans = [pl for pl in plans if pl.get("id") != pid]
    return True

def delete_group(group_id):
    global plans
    gid = int(group_id)
    plans = [pl for pl in plans if pl.get("group_id") != gid]
    return True
