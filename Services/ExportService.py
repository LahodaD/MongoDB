import json
from bson import ObjectId
import base64
from bson import Binary

def convert_to_json_serializable(obj):
    if isinstance(obj, ObjectId):
        return {"$oid": str(obj)}
    elif isinstance(obj, bytes):
        # Speciální formát pro heslo
        return {"$binary": {"base64": base64.b64encode(obj).decode('utf-8'), "subType": "00"}}
    return obj

def export_to_json(db_client, json_filename):
    db = db_client.Library

    all_data = []

    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        cursor = collection.find({})
        documents = list(cursor)

        for document in documents:
            document['_collection'] = collection_name

        all_data.extend(documents)

    with open(json_filename, 'w') as json_file:
        json.dump(all_data, json_file, indent=2, default=convert_to_json_serializable)

    print(f'data from all collections exported to {json_filename}')


def convert_to_python_object(obj):
    if isinstance(obj, dict) and "$binary" in obj:
        binary_data = obj["$binary"]
        base64_string = binary_data["base64"]
        sub_type = int(binary_data["subType"], 16)
        return Binary(base64.b64decode(base64_string), sub_type)
    return obj

def import_data_from_json(db_client, json_filename):
    with open(json_filename, 'r') as json_file:
        data_to_import = json.load(json_file, object_hook=convert_to_python_object)

    for data_item in data_to_import:
        collection_name = data_item.get('_collection', None)
        document = {k: v for k, v in data_item.items() if k != '_collection'}

        if collection_name:
            collection = db_client['Library_Test'][collection_name]

            # Odstraníme existující _id pole, pokud existuje
            document.pop('_id', None)

            # Vytvoříme nový ObjectId a nastavíme ho jako _id dokumentu
            document['_id'] = ObjectId()

            # Přidáme jednotlivý dokument zpět do kolekce
            collection.insert_one(document)
        else:
            print('Chybějící atribut "_collection" ve struktuře JSON souboru.')

    print(f'Data imported to MongoDB collections')
