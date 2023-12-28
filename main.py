from pymongo.mongo_client import MongoClient
import UI
from Repositories import ConnectToDatabase as db
from Repositories import BooksRepository as books_repository


if __name__ == '__main__':
    db_client = db.connect_to_mongodb()

    if db_client is not None:

        #TODO: ukazka pouziti knihovny BooksReposiroty pro vlozeni noveho prvku
        # pak SMAZAT!!!
        #
        # novy_prvek = {
        #     "nazev": "NovyPrvek2",
        #     "hodnota": 42,
        #     "popis": "Toto je novy prvek."
        # }
        # books_repository.insert_document(db_client, novy_prvek)

        #TODO: ukazka najit_vsechno pak SMAZAT!!!
        #
        # for document in books_repository.find_all_documents(db_client):
        #     print(document)

        #TODO: ukazka find_one pak SMAZAT!!!
        #
        # print(books_repository.find_document(db_client, {"Title": "Book1"}))

        root = UI.tk.Tk()
        app = UI.App(root)

        # start UI mainloop
        root.mainloop()
    else:
        print("Error - something wrong with database")
