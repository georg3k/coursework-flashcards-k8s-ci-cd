import pandas as pd
from pymongo import MongoClient
import json


def mongoimport(csv_path, db_name, coll_name, db_url="localhost", db_port=27000):
    """Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    client = MongoClient(db_url, db_port, username="admin", password="pass")
    db = client[db_name]
    data = pd.read_csv(csv_path)

    data["id"] = data["id"].astype(str)
    data["deck"] = data["deck"].astype(str)

    payload = json.loads(data.to_json(orient="records"))
    db.cards.delete_many({})
    db.cards.insert_many(payload)


mongoimport("./hiragana.csv", "flashcards", "cards", "localhost", db_port=27017)
