import base64
import subprocess
import json
import bcrypt
from bson import Binary, ObjectId
from pymongo import MongoClient

def get_all_databases(client):
    return client.list_database_names()

def get_all_collections(client, database_name):
    db = client.get_database(database_name)
    return db.list_collection_names()

def export_all_collections_to_json(client, output_file):
    all_data = {}  # Dictionary to store all data

    databases = get_all_databases(client)

    for database_name in databases:
        if database_name == "Library":        
            collections = get_all_collections(client, database_name)

            if not collections:
                continue

            for collection_name in collections:
                # Query all documents from the collection
                db = client[database_name]
                collection = db[collection_name]
                documents = list(collection.find())

                # Add documents to the dictionary under the database and collection name
                if database_name not in all_data:
                    all_data[database_name] = {}
                all_data[database_name][collection_name] = documents

    # Save the entire dictionary to a single JSON file
    with open(output_file, 'w') as json_file:
        json.dump(all_data, json_file, default=str)
        
        
def import_collections_from_json(client, input_file):
    with open(input_file, 'r') as json_file:
        all_data = json.load(json_file)

        for database_name, collections in all_data.items():
            if database_name == "Library": 
                for collection_name, documents in collections.items():
                    # Get the database and collection
                    db = client[database_name]
                    collection = db[collection_name]

                    # Iterate over documents and update or insert as needed
                    for doc in documents:
                        # Convert _id from string to ObjectId if it's present
                        if '_id' in doc:
                            doc['_id'] = ObjectId(doc['_id'])

                        # Convert Password to binary if it's present
                        if 'Password' in doc:
                            password = doc['Password']
                            if isinstance(password, str):
                                # Assume the password is a bcrypt hash
                                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                                doc['Password'] = Binary(bytes(hashed_password), subtype=0x00)

                        identifier = doc.get("_id")

                        # Use update_one with upsert=True to either update or insert
                        collection.update_one({"_id": identifier}, {"$set": doc}, upsert=True)
