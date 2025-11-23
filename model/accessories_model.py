from utils.db import db

accessories = db["accessories"]

def get_all_accessories():
    return list(accessories.find())

def add_accessory(name, type_):
    item = {"name": name, "type": type_}
    accessories.insert_one(item)
    return item

def remove_accessory(accessory_id):
    accessories.delete_one({"id": accessory_id})
