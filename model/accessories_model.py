"""
accessories_model.py

This file handles all database operations related to accessories in the
StyleForecast application. It follows the Model layer and only deals
with data storage and retrieval.
"""

from utils.db import db
from bson.objectid import ObjectId

# MongoDB collection for storing accessories
accessories = db["accessories"]


def get_all_accessories():
    """
    Retrieve all accessories from the database.

    Converts MongoDB ObjectId to string so the data can be sent
    to the frontend as JSON.
    """

    items = []

    # Loop through all documents in the accessories collection
    for item in accessories.find():
        item["_id"] = str(item["_id"])
        items.append(item)

    return items


def add_accessory(name, type_):
    """
    Add a new accessory to the database.

    Stores basic information like name and type, then returns
    the newly created accessory with its generated ID.
    """

    item = {
        "name": name,
        "type": type_
    }

    result = accessories.insert_one(item)

    # Convert generated ObjectId to string for consistency
    item["_id"] = str(result.inserted_id)

    return item


def remove_accessory(accessory_id):
    """
    Remove an accessory using its unique ID.
    """

    return accessories.delete_one(
        {"_id": ObjectId(accessory_id)}
    )
