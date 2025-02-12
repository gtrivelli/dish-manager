import json
import os

def load_dishes():
    try:
        with open(os.getenv("DATA_FILE"), "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_dishes(dishes):
    with open(os.getenv("DATA_FILE"), "w") as file:
        json.dump(dishes, file, indent=4)