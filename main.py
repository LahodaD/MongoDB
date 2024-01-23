from pymongo.mongo_client import MongoClient
import UI
from Repositories import ConnectToDatabase as db
from Repositories import BooksRepository as books_repository
from Repositories import UsersRepository as users_repository


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

        #TODO: ukazka najit_vsechny_uzivatele pak SMAZAT!!!
        #
        #for document in books_repository.find_all_books(db_client):
        #   print(document)

        #TODO: ukazka find_one pak SMAZAT!!!
        #
        # print(books_repository.find_document(db_client, {"Title": "Book1"}))


        #TODO: ukazka hledani uzivatele se jsmene a prijmenim
        #
        # print(users_repository.find_document(db_client, {"Name": "UserName1", "Surename": "UserSirname1"}))

        #TODO: ukazka vlozeni noveho uzivatele a nove knihy
        #
        #users_repository.create_user(db_client, "Pepa", "Omacka", "0707881010", "Kornvald 12, Praha, Czechia", "Pepa", "1234")
        #books_repository.create_book(db_client,"Kniha", "Daniel Autorsky", "3", "150", "NEMAM", "1859")

        root = UI.tk.Tk()
        app = UI.App(root)

        # start UI mainloop
        root.mainloop()
    else:
        print("Error - something wrong with database")

        