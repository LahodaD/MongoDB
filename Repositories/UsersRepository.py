import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


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


def find_all_documents(db_client):
    return db_client.Library.Users.find()


def find_document(db_client, criteria: dict):
    return db_client.Library.Users.find_one(criteria)


def delete(db_client, criteria: dict):
    return db_client.Library.Users.delete_one(criteria)


def update(db_client, criteria: dict, new_document):
    db_client.Library.Users.update_one(criteria, new_document)
