import datetime

def create_borrowed(db_client, user_id, book_id):
    collection = db_client.Library.Borrowed
    borrowed_document = {
        "UserID": user_id,
        "BookID": book_id,
        "Date": str(datetime.datetime.now())
    }
    result = collection.insert_one(borrowed_document)

    return result.inserted_id

def find_all_documents(db_client):
    return db_client.Library.Borrowed.find()

def find_document(db_client, criteria: dict):
    return db_client.Library.Borrowed.find_one(criteria)

def find_documents(db_client, criteria: dict):
    return db_client.Library.Borrowed.find(criteria)

def delete(db_client, criteria: dict):
    return db_client.Library.Borrowed.delete_one(criteria)

def update(db_client, criteria: dict, new_document):
    db_client.Library.Borrowed.update_one(criteria, new_document)