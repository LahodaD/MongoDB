import datetime
from bson.objectid import ObjectId

def check_number_of_borrowed_books(db_client, user_id):
    number_of_borrowed_books = 0
    collection = db_client.Library.Borrowed
    searchResults = find_documents(db_client,{"UserID": ObjectId(user_id)})
    for books in searchResults:
        number_of_borrowed_books += 1
    return number_of_borrowed_books

def create_borrowed(db_client, user_id, book_id):
    collection = db_client.Library.Borrowed
    borrowed_document = {
        "UserID": ObjectId(user_id),
        "BookID": ObjectId(book_id),
        "Date": str(datetime.datetime.now())
    }
    result = collection.insert_one(borrowed_document)

    return result.inserted_id

def find_all_documents(db_client):
    return db_client.Library.Borrowed.find()

def find_document(db_client, criteria: dict):
    return db_client.Library.Borrowed.find_one(criteria)

def find_document_by_ids(db_client, user_id, book_id):
    return db_client.Library.Borrowed.find_one({"UserID": ObjectId(user_id), "BookID": ObjectId(book_id)})

def find_documents_by_user_id(db_client, user_id):
    return db_client.Library.Borrowed.find({"UserID": ObjectId(user_id)})

def find_documents(db_client, criteria: dict):
    return db_client.Library.Borrowed.find(criteria)

def delete(db_client, criteria: dict):
    return db_client.Library.Borrowed.delete_one(criteria)

def delete_by_id(db_client, borrowed_id):
    return db_client.Library.Borrowed.delete_one({"_id": ObjectId(borrowed_id)})

def update(db_client, criteria: dict, new_document):
    db_client.Library.Borrowed.update_one(criteria, new_document)

def update_by_user_id(db_client, user_id, new_document):
    db_client.Library.Borrowed.update_one({"UserID": ObjectId(user_id)}, new_document)