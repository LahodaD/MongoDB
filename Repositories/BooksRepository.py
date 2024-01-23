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
def create_book(db_client, title, author, copies, pages, picture, year):

    collection = db_client.Library.Books
    bookDocument = {"Title": title,
                    "Author": author,
                    "Copies": int(copies),
                    "Pages": int(pages),
                    "Picture": picture,
                    "Year": int(year),
                    }
    result = collection.insert_one(bookDocument)

    return result.inserted_id

def find_all_documents(db_client):
    return db_client.Library.Books.find()


def find_document(db_client, criteria: dict):
    return db_client.Library.Books.find_one(criteria)


def delete(db_client, criteria: dict):
    return db_client.Library.Books.delete_one(criteria)


def update(db_client, criteria: dict, new_document):
    db_client.Library.Books.update_one(criteria, new_document)
