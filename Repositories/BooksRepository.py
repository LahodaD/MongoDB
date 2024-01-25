from bson.binary import Binary
import re
def insert_document(db_client, document):
    """
    Vloží nový dokument do dané kolekce.

    Parameters:
    - collection: pymongo kolekce, kam bude dokument vložen.
    - document: Slovník obsahující data nového dokumentu.

    Returns:
    - Vrací ID vloženého dokumentu.
    """
    collection = db_client.Library.Books
    result = collection.insert_one(document)
    return result.inserted_id

def create_book(db_client, title, author, genre, pages, year, copies, picture):
    collection = db_client.Library.Books
    book_document = {
        "Title": title,
        "Author": author,
        "Genre": genre,
        "Pages": int(pages),
        "Year": int(year),
        "Copies": int(copies),
        "Picture": Binary(picture),
    }
    result = collection.insert_one(book_document)

    return result.inserted_id

def search_documents(db_client, title, author, genre ):
    queries = []
    if (len(title) >= 3):
        reTitle = re.compile(re.escape(title), re.IGNORECASE)
        queries.append({"Title": {"$regex": reTitle}})
    if (len(author) >= 3):
        reAuthor = re.compile(re.escape(author), re.IGNORECASE)
        queries.append({"Author": {"$regex": reAuthor}})
    if (len(genre) >= 3):
        reGenre = re.compile(re.escape(genre), re.IGNORECASE)
        queries.append({"Genre": {"$regex": reGenre}})
    searchResult = find_documents(db_client, {"$and": queries})
    return searchResult

def find_all_documents(db_client):
    return db_client.Library.Books.find()

def find_document(db_client, criteria: dict):
    return db_client.Library.Books.find_one(criteria)

def find_documents(db_client, criteria: dict):
    return db_client.Library.Books.find(criteria)

def delete(db_client, criteria: dict):
    return db_client.Library.Books.delete_one(criteria)

def update(db_client, criteria: dict, new_document):
    db_client.Library.Books.update_one(criteria, new_document)
