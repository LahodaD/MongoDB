import bcrypt
from bson.objectid import ObjectId

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_passwd(passwd, hashedPassdw):
    if bcrypt.checkpw(passwd.encode('utf-8'), hashedPassdw):
        return True
    return False


def insert_document(db_client, document):
    """
    Vloží nový dokument do dané kolekce.

    Parameters:
    - collection: pymongo kolekce, kam bude dokument vložen.
    - document: Slovník obsahující data nového dokumentu.

    Returns:
    - Vrací ID vloženého dokumentu.
    """

    # Hashuje heslo a pak ho zaheshovane ulozi do db
    document["Password"] = hash_password(document["Password"])

    collection = db_client.Library.Users
    result = collection.insert_one(document)
    return result.inserted_id


def create_user(db_client, name, surename, birthnumber, address, username, password):
    user = db_client.Library.Users.find_one({"Username": username})
    if user is not None:
        return "Username already exists"
    user = db_client.Library.Users.find_one({"BirthNumber": birthnumber})
    if user is not None:
        return "Birth number already in use"

    passwordHash = hash_password(password)
    collection = db_client.Library.Users
    userDocument = {"Name": name,
                    "Surename": surename,
                    "BirthNumber": int(birthnumber),
                    "Address": address,
                    "Username": username,
                    "Password": passwordHash,
                    "Confirmed": False,
                    "Banned": False,
                    "Admin": False,
                    "Borrowed": 0,
                    "History": []}
    result = collection.insert_one(userDocument)

    return result.inserted_id


def find_all_documents(db_client):
    return db_client.Library.Users.find()


def find_document(db_client, criteria: dict):
    return db_client.Library.Users.find_one(criteria)

def find_document_by_id(db_client, user_id):
    return db_client.Library.Users.find_one({"_id": ObjectId(user_id)})

def find_documents(db_client, criteria: dict):
    return db_client.Library.Users.find(criteria)

def delete(db_client, criteria: dict):
    return db_client.Library.Users.delete_one(criteria)

def delete_by_id(db_client, user_id):
    return db_client.Library.Users.delete_one({"_id": ObjectId(user_id)})

def update(db_client, criteria: dict, new_document):
    db_client.Library.Users.update_one(criteria, new_document)

def update_by_user_id(db_client, user_id, new_document):
    db_client.Library.Users.update_one({"_id": ObjectId(user_id)}, new_document)


def get_value_of_field_by_id(db_client, user_id, field_name: str):
    temporery_document = find_document_by_id(db_client, user_id)
    return temporery_document[field_name]
