# model/accessories_model.py
from utils.db import db
from bson.objectid import ObjectId

accessories = db["accessories"]

def get_all_accessories():
    items = []
    for item in accessories.find():
        item["_id"] = str(item["_id"])  # convert for JSON
        items.append(item)
    return items

def add_accessory(name, type_):
    item = {"name": name, "type": type_}
    result = accessories.insert_one(item)
    item["_id"] = str(result.inserted_id)
    return item

def remove_accessory(accessory_id):
    return accessories.delete_one({"_id": ObjectId(accessory_id)})
