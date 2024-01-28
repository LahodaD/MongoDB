from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

from Repositories.BooksRepository import create_book
from Repositories import ConnectToDatabase as db
from Repositories import BooksRepository as books_repository
from Repositories import UsersRepository as users_repository
from Repositories import BorrowedRepository as borrowed_repository

class App:
    db_client = db.connect_to_mongodb()
    books = [("Book1", "Author1", "Genre1", 5), ("Book2", "Author2", "Genre2", 3), ("Book3", "Author3", "Genre3", 7)]


    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.resizable(False, False)
        self.root.attributes("-toolwindow", 1)
        self.center_window()
        self.create_login_frame()        
        self.image_path = None

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        #x = (screen_width - self.root.winfo_reqwidth()) // 2
        #y = (screen_height - self.root.winfo_reqheight()) // 2
        x = (screen_width//2) -401
        y = (screen_height//2) -140
        self.root.geometry("+{}+{}".format(x, y))

    #Login okno
    #TODO: přidat button pro registraci, přidat okno pro registraci
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()

        self.label_username = tk.Label(self.login_frame, text="Username:")
        self.label_password = tk.Label(self.login_frame, text="Password:")

        self.entry_username = tk.Entry(self.login_frame)
        self.entry_password = tk.Entry(self.login_frame, show="*")

        self.label_username.grid(row=0, column=0)
        self.label_password.grid(row=1, column=0)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2)

        self.register_button = tk.Button(self.login_frame, text="Register", command=self.show_registration_window)
        self.register_button.grid(row=3, columnspan=2)

    #Login funkce
    def login(self):
        global currentUser
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = users_repository.find_document(self.db_client,{"Username": username})
        if not user:
            return False
        if user["Banned"]:
            return False
        if users_repository.check_passwd(password, user["Password"]):
            currentUser = user
            if user["Admin"]:
                self.show_admin_layout()
            else:
                self.show_customer_layout()
        else:
            print("does not match")
            messagebox.showerror("Login Failed", "Invalid username or password")


    def show_registration_window(self):
        self.registration_window = tk.Toplevel(self.root)
        self.registration_window.title("Registration")

        self.label_name = tk.Label(self.registration_window, text="Name:")
        self.label_surname = tk.Label(self.registration_window, text="Surname:")
        self.label_birthdate = tk.Label(self.registration_window, text="Birthnumber:")
        self.label_adress = tk.Label(self.registration_window, text="Adress:")
        self.label_reg_username = tk.Label(self.registration_window, text="Username:")
        self.label_reg_password = tk.Label(self.registration_window, text="Password:")

        self.entry_name = tk.Entry(self.registration_window)
        self.entry_surname = tk.Entry(self.registration_window)
        self.entry_birthdate = tk.Entry(self.registration_window)
        self.entry_adress = tk.Entry(self.registration_window)
        self.entry_reg_username = tk.Entry(self.registration_window)
        self.entry_reg_password = tk.Entry(self.registration_window, show="*")

        self.label_name.grid(row=0, column=0)
        self.label_surname.grid(row=1, column=0)
        self.label_birthdate.grid(row=2, column=0)
        self.label_adress.grid(row=3, column=0)
        self.label_reg_username.grid(row=4, column=0)
        self.label_reg_password.grid(row=5, column=0)

        self.entry_name.grid(row=0, column=1)
        self.entry_surname.grid(row=1, column=1)
        self.entry_birthdate.grid(row=2, column=1)
        self.entry_adress.grid(row=3, column=1)
        self.entry_reg_username.grid(row=4, column=1)
        self.entry_reg_password.grid(row=5, column=1)

        register_button = tk.Button(self.registration_window, text="Register", command=self.register)
        register_button.grid(row=6, columnspan=2)

    def register(self):
        #TODO: naházet inputy do DB
        name = self.entry_name.get()
        surname = self.entry_surname.get()
        birthdate = self.entry_birthdate.get()
        adress = self.entry_adress.get()
        username = self.entry_reg_username.get()
        password = self.entry_reg_password.get()

        if not (len(name) >= 1) and (len(surname) >= 1) and (len(birthdate) >= 1) and (len(adress) >= 1) and (len(username) >= 1) and (len(password) >= 1):
            self.show_error_message("Each input has to have atleast 3 characters or be empty.")
            return

        users_repository.create_user(self.db_client,name,surname,birthdate,adress,username,password)
        # Zavření okna registrace
        self.registration_window.destroy()

#Konec inicializace UI a loginu
######################################################################################################################
#Admin layout a funkce s ním spojené
#TODO: přidat button zobrazující list čekajících úprav profilu a nových registrací, přidat dvojklikem možnost rozbalení knihy a upravení jejich parametrů
    
    #Admin layout
    def show_admin_layout(self):
        self.login_frame.destroy()
        admin_frame = tk.Frame(self.root, width=1220, height=280)
        admin_frame.pack()

        #Pozice tlačítka je řešena později
        logout_button = tk.Button(admin_frame, text="Logout", command=self.logout)

        #Definování sloupců u treeview
        columns = ("Id","Title", "Author", "Genre", "Pages", "Year", "Copies")
        self.sort_order = {col: True for col in columns}  #Keep track of sorting order (sestupně/vzestupně)

        self.admin_tree = ttk.Treeview(admin_frame, columns=columns, show="headings")

        for col in columns:
            self.admin_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        for col in columns:
            if col == "Id":
                self.admin_tree.column(col, stretch="no", minwidth=0, width=0)
                continue
            self.admin_tree.column(col, stretch="yes", minwidth=0, width=200)

        self.admin_tree.place(x=0,y=40 + 15)



        logout_button.place(x=(self.admin_tree.winfo_reqwidth()-logout_button.winfo_reqwidth()),y=0)

        #Plnění treeview daty z databáze
        for document in books_repository.find_all_documents(self.db_client):
            books_data = ((document["_id"],document["Title"], document["Author"], document["Genre"], document["Pages"], document["Year"], document["Copies"]))
            self.admin_tree.insert("", "end", values=books_data)


        #Delete button maže vybrané prvky v treeview
        delete_button = tk.Button(admin_frame, text="Delete", command=self.delete_selected, width=6)
        delete_button.place(x=(self.admin_tree.winfo_reqwidth()-logout_button.winfo_reqwidth()),y=logout_button.winfo_reqheight())


        #Add button přidává knihy nebo zvyšuje počet kopií
        add_button = tk.Button(admin_frame, text="Add Book", command=self.show_add_window)
        add_button.place(x=(self.admin_tree.winfo_reqwidth()-delete_button.winfo_reqwidth()-add_button.winfo_reqwidth()-5), y=logout_button.winfo_reqheight())

        #Button pro vyhledávání v treeview
        search_button = tk.Button(admin_frame, text="Search", command=self.show_search_window)
        search_button.place(x=(self.admin_tree.winfo_reqwidth()-delete_button.winfo_reqwidth()-add_button.winfo_reqwidth()-5), y=0)

        #Zrušení omezení vyhledávání
        cancel_search_button = tk.Button(admin_frame, text="Cancel Search", command=self.cancel_search)
        cancel_search_button.place(x=(self.admin_tree.winfo_reqwidth()-logout_button.winfo_reqwidth()-add_button.winfo_reqwidth()-cancel_search_button.winfo_reqwidth()-15), y=0)

        #Zobrazení okna s informacemi uživatele
        user_info_button = tk.Button(admin_frame, text="User info", command=self.show_user_info)
        user_info_button.place(x=(self.admin_tree.winfo_reqwidth()-logout_button.winfo_reqwidth()-add_button.winfo_reqwidth()-cancel_search_button.winfo_reqwidth()-user_info_button.winfo_reqwidth()-20), y=0)

        #půjčení knihy
        borrow_book_button = tk.Button(admin_frame, text="Borrow book", command=self.borrow_book)
        borrow_book_button.place(x=( self.admin_tree.winfo_reqwidth() - logout_button.winfo_reqwidth() - add_button.winfo_reqwidth() - cancel_search_button.winfo_reqwidth() - 15),
                                 y=logout_button.winfo_reqheight())

        #view půjčených knih
        borrow_view_button = tk.Button(admin_frame, text="Borrowed books", command=self.show_borrowed_layout)
        borrow_view_button.place(x=( self.admin_tree.winfo_reqwidth() - logout_button.winfo_reqwidth() - add_button.winfo_reqwidth() - cancel_search_button.winfo_reqwidth() - -user_info_button.winfo_reqwidth()- borrow_book_button.winfo_reqwidth() - borrow_view_button.winfo_reqwidth()),
                                 y=logout_button.winfo_reqheight())

        # Zobrazení okna s informacemi uživatele
        users_button = tk.Button(admin_frame, text="Users", command=self.show_users_layout)
        users_button.place(x=(
                    self.admin_tree.winfo_reqwidth() - logout_button.winfo_reqwidth() - add_button.winfo_reqwidth() - cancel_search_button.winfo_reqwidth() - user_info_button.winfo_reqwidth() - users_button.winfo_reqwidth()- 20),
                               y=0)

    #-------------------------------------------------------------------------------------------------------------------------
#Konec admin layoutu, níže jsou funkce pro admin layout
#-------------------------------------------------------------------------------------------------------------------------

    #Vymaže vybranou knihu z treeview
    #TODO: implementovat mazání z databáze
    def delete_selected(self):
        # Seznam vybraných řádků
        selected_items = self.admin_tree.selection()

        #Mazání jednotlivých itemů
        for item in selected_items:
            id_of_book =  tuple(self.admin_tree.item(item, "values"))[0]
            borrowed = borrowed_repository.find_document_by_book_id(self.db_client, id_of_book)
            if borrowed is not None:
                print("book is borrowed")
                messagebox.showerror("Book is borrowed", "Book can not be deletet. This book is borrowed")
                return False
            books_repository.delete_by_id(self.db_client, id_of_book)

        self.cancel_search()


    def borrow_book(self):
        #Seznam vybraných řádků
        selected_items = self.admin_tree.selection()
        current_user_info = users_repository.find_document_by_id(self.db_client,currentUser["_id"])
        #kontrola počtu vypůjčených knih
        if current_user_info["Borrowed"] >= 6:
            print("too many borrowed books")
            messagebox.showerror("Too many borrowed books", "You have too many borrowed books (6 books)")
            return False
        if not current_user_info["Confirmed"]:
            print("not confirmed")
            messagebox.showerror("Not confirmed", "Your account is not confirmed")
            return False

        #vypůjčování knížky
        for item in selected_items:
            id_of_book = tuple(self.admin_tree.item(item, "values"))[0]
            #kontrola jestli ji již má vypůjčenou
            borrowed = borrowed_repository.find_document_by_ids(self.db_client, currentUser["_id"], id_of_book)
            if borrowed is not None:
                print("already borrowed")
                messagebox.showerror("Already borrowed", "You have a copie of this book already borrowed")
                return False
            if books_repository.get_value_of_field_by_id(self.db_client, id_of_book, "Copies") <= 0:
                print("not enough copies")
                messagebox.showerror("Not enough copies", "Not enough copies to borrow")
                return False
            print("borrowing")
            #vypujčování
            borrowed_repository.create_borrowed(self.db_client, currentUser["_id"], id_of_book)
            #přepis počtu kopií
            books_repository.update_by_book_id(self.db_client, id_of_book, {"$set": {"Copies" : books_repository.get_value_of_field_by_id(self.db_client, id_of_book, "Copies") - 1}})
            #přepis počtu vypůjčených knih u usera
            users_repository.update_by_user_id(self.db_client,  currentUser["_id"], {"$set": {"Borrowed": borrowed_repository.check_number_of_borrowed_books(self.db_client,currentUser["_id"]) }})
            #načtení historie
            user_history = users_repository.get_value_of_field_by_id(self.db_client, currentUser["_id"], "History")
            #zapsání do historie lokálně
            user_history.append(tuple(self.admin_tree.item(item, "values"))[1])
            print(user_history)
            #nahrání historie na DB
            users_repository.update_by_user_id(self.db_client, currentUser["_id"], {"$set": {"History": user_history}})
        #refresh
        self.cancel_search()


    #Třídění treeview, první sestupně, po druhém kliku vzestupně atd.
    #TODO: implementovat to na straně databáze a zde to jen natáhnout do treeview
    def sort_treeview(self, column):

        #Get all items in the treeview and sort them based on the selected column
        items = self.admin_tree.get_children("")
        items = sorted(items, key=lambda i: self.admin_tree.set(i, column), reverse=self.sort_order[column])

        #Rearrange the items in the treeview
        for i, item in enumerate(items):
            self.admin_tree.move(item, "", i)

        #Toggle the sorting order for the next click
        self.sort_order[column] = not self.sort_order[column]

    def show_add_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Book")
        add_window.geometry("580x350")
        add_window.minsize(580, 350)

        labels = ["Title", "Author", "Genre", "Pages", "Year", "Number of Copies"]
        entries = {}

        for i, label_text in enumerate(labels):
            label = tk.Label(add_window, text=f"{label_text}:")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            entry = tk.Entry(add_window)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            entries[label_text.lower()] = entry

        # Button for selecting an image
        select_picture_button = tk.Button(add_window, text="Select Image", command=lambda: self.browse_image(add_window), width=80)
        select_picture_button.grid(row=len(labels), column=0, padx=5, pady=5, sticky="ew", columnspan=4)

        # Update grid row, column, columnspan, and sticky options for confirm_button
        confirm_button = tk.Button(add_window, text="Confirm", command=lambda: self.add_book(
            entries["title"].get(), entries["author"].get(), entries["genre"].get(), entries["pages"].get(),
            entries["year"].get(), entries["number of copies"].get(), add_window), width=80)
        confirm_button.grid(row=len(labels) + 1, column=0, padx=5, pady=10, sticky="ew", columnspan=4)

        # Create a Label widget to display the selected image
        image_label = tk.Label(add_window, text="Image Preview")
        image_label.grid(row=0, column=2, pady=5, sticky="ew", columnspan=1)
        image_label.config(width=20, height=8)  # Adjust size as needed
        image_label.grid_propagate(False)

        # Configure row and column options
        for i in range(len(labels) + 3):
            add_window.grid_rowconfigure(i, weight=1)

        add_window.grid_columnconfigure(0, weight=1)
        add_window.grid_columnconfigure(1, weight=1)

    def browse_image(self, add_window): 
        # Open a file dialog to select an image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])

        if file_path:
            # Update the image path entry and preview the image
            self.image_path = file_path
            self.show_image_preview(file_path, add_window)

    def show_image_preview(self, image_path, add_window):   
        try:
            # Open the image using PIL
            img = Image.open(image_path)
            img.thumbnail((160, 160))  # Adjust size if needed
    
            # Convert the PIL Image to a Tkinter PhotoImage
            tk_img = ImageTk.PhotoImage(img)
    
            # Create a new frame for displaying the image (inside add_window)
            image_frame = tk.Frame(add_window)
            image_frame.grid(row=0, column=2, rowspan=6, columnspan=6, padx=5, pady=5, sticky="ne")
    
            # Create a Canvas widget within the new frame to display the image
            canvas = tk.Canvas(image_frame, width=160, height=160)  # Adjust size as needed
            canvas.grid(row=0, column=0, sticky="nw")
    
            # Draw the image on the Canvas
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
    
            # Keep a reference to the PhotoImage to prevent garbage collection
            canvas.image = tk_img
    
        except Exception as e:
            # Handle the case where the image couldn't be loaded
            print(f"Error loading image: {e}")

    
    #Okno pro hledání knih
    def show_search_window(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Books")

        title_label = tk.Label(search_window, text="Title:")
        title_label.grid(row=0, column=0, padx=5, pady=5)
        title_entry = tk.Entry(search_window)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        author_label = tk.Label(search_window, text="Author:")
        author_label.grid(row=1, column=0, padx=5, pady=5)
        author_entry = tk.Entry(search_window)
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        genre_label = tk.Label(search_window, text="Genre:")
        genre_label.grid(row=2, column=0, padx=5, pady=5)
        genre_entry = tk.Entry(search_window)
        genre_entry.grid(row=2, column=1, padx=5, pady=5)

        #Tlačítko confirm vezme inputy a  zavolá funkci search_books
        confirm_button = tk.Button(search_window, text="Confirm", command=lambda: self.search_books(
            title_entry.get(), author_entry.get(), genre_entry.get(), search_window))
        confirm_button.grid(row=3, column=0, columnspan=2, pady=10)

    #Funkce pro hledání knihy, kontroluje minimální délku inputů
    #TODO: ošetřit velikost vstupu
    def search_books(self, title, author, genre, search_window):
        #Kontrola jestli jsou v inputech alespoň 3 znaky nebo jsou null
        if not (len(title) >= 3 or len(title)==0) and (len(author) >= 3 or len(author)==0) and (len(genre) >= 3 or len(genre)==0):
            messagebox.showerror("Filed needs to be 3 or more", "Filed needs to be 3 or more characters")
            return
        #Kontrola jestli všechny inputy nejsou null
        if (len(title)==0 and len(author)==0 and len(genre)==0):
            messagebox.showerror("No valid input", "No valid inputs for search")
            return
        
        #Clear existing items in the treeview
        self.admin_tree.delete(*self.admin_tree.get_children())

        #Filter books based on search criteria
        searchResult = books_repository.search_documents(self.db_client,title,author,genre)
        #searchResult = books_repository.find_documents(self.db_client, {"$and": queries})
        for book in searchResult:
            if(book == None):
                return
            book_data = ((book["_id"],book["Title"], book["Author"], book["Genre"], book["Pages"], book["Year"], book["Copies"]))
            self.admin_tree.insert("", "end", values=book_data)


        #Close the search window
        search_window.destroy()

    #Funkce cancel search opět zobrazí vše ve výběru
    def cancel_search(self):
        #Clear search criteria and display all books
        self.admin_tree.delete(*self.admin_tree.get_children())
        for document in books_repository.find_all_documents(self.db_client):
            books_data = ((document["_id"],document["Title"], document["Author"], document["Genre"], document["Pages"], document["Year"], document["Copies"]))
            self.admin_tree.insert("", "end", values=books_data)

    #Funkce pro přidávání knih
    #TODO: přidání knihy do databáze a následné natáhnutí selectu z databáze do treeview (stejné jak u mazání)
    def add_book(self, title, author, genre, pages, year, copies, add_window):
        try:
            # Convert the image to bytes
            image_bytes = self.convert_image_to_bytes()

            # Call create_book function to save data in the database
            document_id = create_book(
                self.db_client,
                title=title,
                author=author,
                genre=genre,
                pages=int(pages),  # Assuming pages is an integer
                year=int(year),    # Assuming year is an integer
                copies=int(copies),  # Assuming copies is an integer
                picture=image_bytes,
            )

            # If the book already exists, update the number of copies
            existing_item = None
            for item in self.admin_tree.get_children():
                if (
                    self.admin_tree.item(item, "values")[0] == title
                    and self.admin_tree.item(item, "values")[1] == author
                ):
                    existing_item = item
                    break

            if existing_item:
                # If the book already exists, update the number of copies
                current_copies = int(self.admin_tree.item(existing_item, "values")[3])
                new_copies = current_copies + int(copies)
                self.admin_tree.item(
                    existing_item,
                    values=(title, author, self.admin_tree.item(existing_item, "values")[2], new_copies),
                )

                App.books = []
                for item in self.admin_tree.get_children():
                    book_data = tuple(self.admin_tree.item(item, "values"))
                    App.books.append(book_data)
            else:
                # If the book does not exist, add a new row
                self.admin_tree.insert("", "end", values=(title, author, genre,int(year), int(pages), int(copies)))

                App.books = []
                for item in self.admin_tree.get_children():
                    book_data = tuple(self.admin_tree.item(item, "values"))
                    App.books.append(book_data)

            # Close the add window
            add_window.destroy()

        except Exception as e:
            # Handle the case where there is an error saving the book
            self.show_error_message(f"Error adding book: {e}")

    def convert_image_to_bytes(self):
        try:
            if self.image_path:
                # Convert the PIL Image to bytes
                img = Image.open(self.image_path)
                img_bytes = BytesIO()
                img.save(img_bytes, format="PNG")
                return img_bytes.getvalue()
        except Exception as e:
            print(f"Error converting image to bytes: {e}")
        return None

    #Funkce pro ukazování error zpráv
    def show_error_message(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        tk.Label(error_window, text=message).pack()
        tk.Button(error_window, text="OK", command=error_window.destroy).pack()

    def show_user_info(self):
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("User information")

        label_name = tk.Label(self.info_window, text="Name:")
        label_surname = tk.Label(self.info_window, text="Surname:")
        label_birthdate = tk.Label(self.info_window, text="Birthdate:")
        label_adress = tk.Label(self.info_window, text="Adress:")
        label_info_username = tk.Label(self.info_window, text="Username:")
        label_info_password = tk.Label(self.info_window, text="Password:")

        entry_name = tk.Entry(self.info_window)
        entry_surname = tk.Entry(self.info_window)
        entry_birthdate = tk.Entry(self.info_window)
        entry_adress = tk.Entry(self.info_window)
        entry_info_username = tk.Entry(self.info_window)
        entry_info_password = tk.Entry(self.info_window, show="*")

        label_name.grid(row=0, column=0)
        label_surname.grid(row=1, column=0)
        label_birthdate.grid(row=2, column=0)
        label_adress.grid(row=3, column=0)
        label_info_username.grid(row=4, column=0)
        label_info_password.grid(row=5, column=0)

        entry_name.grid(row=0, column=1)
        entry_surname.grid(row=1, column=1)
        entry_birthdate.grid(row=2, column=1)
        entry_adress.grid(row=3, column=1)
        entry_info_username.grid(row=4, column=1)
        entry_info_password.grid(row=5, column=1)

        #TODO: zobrazit info uzivatele
        #Místo "" hodit co info z DB nebo tabulky (prozatím jsou tam fešné placeholdery)
        user_info = users_repository.find_document_by_id(self.db_client, currentUser["_id"])
        entry_name.insert(0, user_info["Name"])
        entry_surname.insert(0, user_info["Surename"])
        entry_birthdate.insert(0, user_info["BirthNumber"])
        entry_adress.insert(0, user_info["Address"])
        entry_info_username.insert(0, user_info["Username"])
        #Password pole je necháno prázné

        confirm_button = tk.Button(self.info_window, text="Confirm", command=lambda: self.check_changes(
                entry_name.get(),
                entry_surname.get(),
                entry_birthdate.get(),
                entry_adress.get(),
                entry_info_username.get(),
                entry_info_password.get()
            ))
        confirm_button.grid(row=6, columnspan=2)


    def check_changes(self, name, surname, birthdate,adress, info_username, info_password):
        #TODO: implementovat zmeny infa o uzivately
        user_info = users_repository.find_document_by_id(self.db_client, currentUser["_id"])
        #Je tu jen hodne hodne hruby nastrel
        if any([
            name != "",
            surname != "",
            birthdate != "",
            adress != "",
            info_username != ""
        ]):
            if info_username != user_info["Username"]:
                user = self.db_client.Library.Users.find_one({"Username": info_username})
                if user is not None:
                    return "Username already exists"
            # Changes were made, show confirmation message
            confirmation_message = f"Do you want to apply changes for user {info_username}?"
            result = messagebox.askyesnocancel("Confirmation", confirmation_message)

            if result is not None:
                if result:  # Yes
                    if any([
                        name == "",
                        surname == "",
                        birthdate == "",
                        info_username == ""#,
                        #info_password == "",
                    ]):
                        self.show_error_message("All inputs must be filled.")
                    else:
                        if info_password == "":
                            users_repository.edit_by_user_id_no_passwd(self.db_client, currentUser["_id"], name, surname, birthdate, adress, info_username)
                        else:
                            users_repository.edit_by_user_id(self.db_client, currentUser["_id"], name, surname, birthdate, adress, info_username, info_password)

                        print(f"User data updated for user {info_username}")
                        self.info_window.destroy()
                        
                elif not result:  # No
                    self.info_window.destroy()
                #else:
                    #show_user_info.destroy()
        else:
            self.info_window.destroy()
            


#Konec admin layoutu a funkcí
######################################################################################################################
    def show_borrowed_layout(self):
        borrowed_window = tk.Toplevel(self.root)
        borrowed_window.title("Borrowed Book")
        borrowed_window.geometry("1220x280")
        borrowed_window.minsize(1220, 280)

        #Pozice tlačítka je řešena později
        borrowed_return_button = tk.Button(borrowed_window, text="Return", command=self.return_book)

        #Definování sloupců u treeview
        columns = ("Id","UserID", "BookID","Username", "Title", "Author", "Genre", "Year")
        self.sort_order = {col: True for col in columns}  #Keep track of sorting order (sestupně/vzestupně)

        self.borrowed_tree = ttk.Treeview(borrowed_window, columns=columns, show="headings")

        for col in columns:
            self.borrowed_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        for col in columns:
            if col == "Id" or col == "UserID" or col == "BookID":
                self.borrowed_tree.column(col, stretch="no", minwidth=0, width=0)
                continue
            self.borrowed_tree.column(col, stretch="yes", minwidth=0, width=200)

        self.borrowed_tree.place(x=0,y=40 + 15)



        borrowed_return_button.place(x=(self.borrowed_tree.winfo_reqwidth()-borrowed_return_button.winfo_reqwidth()),y=0)

        #Plnění treeview daty z databáze
        if(currentUser["Admin"]):
            for document in borrowed_repository.find_all_documents(self.db_client):
                book_data = books_repository.find_document_by_id(self.db_client,document["BookID"] )
                user_data = users_repository.find_document_by_id(self.db_client,document["UserID"] )
                books_data = ((document["_id"],document["UserID"], document["BookID"],user_data["Username"], book_data["Title"], book_data["Author"], book_data["Genre"], book_data["Year"]))
                self.borrowed_tree.insert("", "end", values=books_data)
        else:
            for document in borrowed_repository.find_documents_by_user_id(self.db_client,currentUser["_id"]):
                book_data = books_repository.find_document_by_id(self.db_client,document["BookID"] )
                user_data = users_repository.find_document_by_id(self.db_client,document["UserID"] )
                books_data = ((document["_id"],document["UserID"], document["BookID"],user_data["Username"], book_data["Title"], book_data["Author"], book_data["Genre"], book_data["Year"]))
                self.borrowed_tree.insert("", "end", values=books_data)


        #Delete button maže vybrané prvky v treeview
        borrowed_refresh_button = tk.Button(borrowed_window, text="Refresh", command=self.borrowed_refresh, width=6)
        borrowed_refresh_button.place(x=(self.borrowed_tree.winfo_reqwidth()-borrowed_return_button.winfo_reqwidth()),y=borrowed_return_button.winfo_reqheight())



# -------------------------------------------------------------------------------------------------------------------------
# Konec borrowed layoutu, níže jsou funkce pro borrowed layout
# -------------------------------------------------------------------------------------------------------------------------
    def return_book(self):
        # Seznam vybraných řádků
        selected_items = self.borrowed_tree.selection()

        # vracení knížky
        for item in selected_items:
            id_of_book = tuple(self.borrowed_tree.item(item, "values"))[2]
            id_of_user =  tuple(self.borrowed_tree.item(item, "values"))[1]
            id_of_borrowed  = tuple(self.borrowed_tree.item(item, "values"))[0]
            copies_of_book = books_repository.get_value_of_field_by_id(self.db_client, id_of_book, "Copies")
            copies_of_book = copies_of_book + 1
            # přepis počtu kopií
            books_repository.update_by_book_id(self.db_client, id_of_book, {"$set": {"Copies":copies_of_book}})
            #mazání vypůjčení
            borrowed_repository.delete_by_id(self.db_client, id_of_borrowed)

            # přepis počtu vypůjčených knih u usera
            users_repository.update_by_user_id(self.db_client, id_of_user, {"$set": {
                "Borrowed": borrowed_repository.check_number_of_borrowed_books(self.db_client, currentUser["_id"])}})
        # refresh
        self.borrowed_refresh()


    def borrowed_refresh(self):
        self.borrowed_tree.delete(*self.borrowed_tree.get_children())
        if(currentUser["Admin"]):
            for document in borrowed_repository.find_all_documents(self.db_client):
                book_data = books_repository.find_document_by_id(self.db_client,document["BookID"] )
                user_data = users_repository.find_document_by_id(self.db_client,document["UserID"] )
                books_data = ((document["_id"],document["UserID"], document["BookID"],user_data["Username"], book_data["Title"], book_data["Author"], book_data["Genre"], book_data["Year"]))
                self.borrowed_tree.insert("", "end", values=books_data)
        else:
            for document in borrowed_repository.find_documents_by_user_id(self.db_client,currentUser["_id"]):
                book_data = books_repository.find_document_by_id(self.db_client,document["BookID"] )
                user_data = users_repository.find_document_by_id(self.db_client,document["UserID"] )
                books_data = ((document["_id"],document["UserID"], document["BookID"],user_data["Username"], book_data["Title"], book_data["Author"], book_data["Genre"], book_data["Year"]))
                self.borrowed_tree.insert("", "end", values=books_data)

        # Konec borrow layoutu a funkcí
        ######################################################################################################################

    # User layout
    def show_users_layout(self):
        users_window = tk.Toplevel(self.root)
        users_window.title("Users Book")
        users_window.geometry("1300x280")
        users_window.minsize(1300, 280)

        # Pozice tlačítka je řešena později
        users_confirm_button = tk.Button(users_window, text="Confirm", command=self.users_confirm)

        # Definování sloupců u treeview
        columns = ("Id", "Name", "Surename", "Birth number", "Address", "Username", "Confirmed", "Banned", "Borrowed")
        self.sort_order = {col: True for col in columns}  # Keep track of sorting order (sestupně/vzestupně)

        self.users_tree = ttk.Treeview(users_window, columns=columns, show="headings")

        for col in columns:
            self.users_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        for col in columns:
            if col == "Id":
                self.users_tree.column(col, stretch="no", minwidth=0, width=0)
                continue
            if col == "Confirmed" or col == "Banned" or col == "Borrowed":
                self.users_tree.column(col, stretch="no", minwidth=0, width=80)
                continue
            self.users_tree.column(col, stretch="yes", minwidth=0, width=200)

        self.users_tree.place(x=0, y=40 + 15)

        users_confirm_button.place(
            x=(self.users_tree.winfo_reqwidth() - users_confirm_button.winfo_reqwidth()), y=0)

        # Plnění treeview daty z databáze
        for document in users_repository.find_all_documents(self.db_client):
            users_data = ((
            document["_id"], document["Name"], document["Surename"], document["BirthNumber"], document["Address"],
            document["Username"], document["Confirmed"], document["Banned"], document["Borrowed"]))
            self.users_tree.insert("", "end", values=users_data)

         # Delete button maže vybrané prvky v treeview
        users_delete_button = tk.Button(users_window, text="Delete", command=self.users_delete, width=6)
        users_delete_button.place(x=(self.users_tree.winfo_reqwidth() - users_confirm_button.winfo_reqwidth()),
                                y=users_confirm_button.winfo_reqheight())

        #Add button přidává knihy nebo zvyšuje počet kopií
        users_edit_button = tk.Button(users_window, text="Edit", command=self.show_selected_user_info)
        users_edit_button.place(x=(self.users_tree.winfo_reqwidth()-users_delete_button.winfo_reqwidth()-users_edit_button.winfo_reqwidth()-5), y=users_confirm_button.winfo_reqheight())

        #Button pro vyhledávání v treeview
        users_bann_button = tk.Button(users_window, text="Bann", command=self.users_bann)
        users_bann_button.place(x=(self.users_tree.winfo_reqwidth()-users_delete_button.winfo_reqwidth()-users_edit_button.winfo_reqwidth()-5), y=0)

        #Zrušení omezení vyhledávání
        users_borrow_for_button = tk.Button(users_window, text="Borrow for", command=self.users_borrow_for)
        users_borrow_for_button.place(x=(self.users_tree.winfo_reqwidth()-users_confirm_button.winfo_reqwidth()-users_edit_button.winfo_reqwidth()-users_borrow_for_button.winfo_reqwidth()-15), y=0)

        users_create_user_button = tk.Button(users_window, text="Create user", command=self.users_create_user)
        users_create_user_button.place(x=(self.users_tree.winfo_reqwidth()-users_confirm_button.winfo_reqwidth()-users_edit_button.winfo_reqwidth()-users_borrow_for_button.winfo_reqwidth()-users_create_user_button.winfo_reqwidth()-15), y=0)




    # -------------------------------------------------------------------------------------------------------------------------
    # Konec borrowed layoutu, níže jsou funkce pro borrowed layout
    # ------------------------
    #
    #
    # -------------------------------------------------------------------------------------------------

    def users_confirm(self):
        selected_items = self.users_tree.selection()

        # změna statusu potvrzení uživatele
        for item in selected_items:
            id_of_user =  tuple(self.users_tree.item(item, "values"))[0]

            confirmed_status = users_repository.get_value_of_field_by_id(self.db_client, id_of_user, "Confirmed")
            confirmed_status = not confirmed_status
            # přepis potvrzení
            users_repository.update_by_user_id(self.db_client, id_of_user, {"$set": {"Confirmed": confirmed_status}})
        self.users_refresh()
        return False

    def users_refresh(self):
        self.users_tree.delete(*self.users_tree.get_children())
        for document in users_repository.find_all_documents(self.db_client):
            users_data = ((
            document["_id"], document["Name"], document["Surename"], document["BirthNumber"], document["Address"],
            document["Username"], document["Confirmed"], document["Banned"] , document["Borrowed"]))
            self.users_tree.insert("", "end", values=users_data)
        return False

    def users_delete(self):
        selected_items = self.users_tree.selection()

        # změna statusu bannování
        for item in selected_items:
            id_of_user =  tuple(self.users_tree.item(item, "values"))[0]
            print(id_of_user)
            borrowed = borrowed_repository.find_document_by_user_id(self.db_client, id_of_user)
            print(borrowed)
            if borrowed is not None:
                print("user has a book borrowed")
                messagebox.showerror("User has a book borrowed", "User can not be deleted. User has a book borrowed")
                return False
            users_repository.delete_by_id(self.db_client,id_of_user)

        self.users_refresh()

        return False


    def users_bann(self):
        selected_items = self.users_tree.selection()

        # změna statusu bannování
        for item in selected_items:
            id_of_user =  tuple(self.users_tree.item(item, "values"))[0]

            banned_status = users_repository.get_value_of_field_by_id(self.db_client, id_of_user, "Banned")
            banned_status = not banned_status
            # přepis bannování
            users_repository.update_by_user_id(self.db_client, id_of_user, {"$set": {"Banned": banned_status}})
        self.users_refresh()
        return False

    def users_borrow_for(self):
        user_id = ""
        user_name = ""
        book_id = ""
        book_name = ""
        selected_items = self.users_tree.selection()
        for item in selected_items:
            user_id = tuple(self.users_tree.item(item, "values"))[0]
            user_name = tuple(self.users_tree.item(item, "values"))[5]
        selected_items = self.admin_tree.selection()
        for item in selected_items:
            book_id = tuple(self.admin_tree.item(item, "values"))[0]
            book_name = tuple(self.admin_tree.item(item, "values"))[1]

        if user_id == "" or book_id == "":
            print("not selected user and a book")
            messagebox.showerror("Error", "You did not select user and book for the user")
            return False

        slected_user_info = users_repository.find_document_by_id(self.db_client,user_id)
        #kontrola počtu vypůjčených knih
        if slected_user_info["Borrowed"] >= 6:
            print("too many borrowed books")
            messagebox.showerror("Too many borrowed books", "You have too many borrowed books (6 books)")
            return False
        if not slected_user_info["Confirmed"]:
            print("not confirmed")
            messagebox.showerror("Not confirmed", "Your account is not confirmed")
            return False

        borrowed = borrowed_repository.find_document_by_ids(self.db_client, user_id, book_id)
        if borrowed is not None:
            print("already borrowed")
            messagebox.showerror("Already borrowed", "User has a copie of this book already borrowed")
            return False
        if books_repository.get_value_of_field_by_id(self.db_client, book_id, "Copies") <= 0:
            print("not enough copies")
            messagebox.showerror("Not enough copies", "Not enough copies to borrow")
            return False

        borrowed_repository.create_borrowed(self.db_client, user_id, book_id)

        books_repository.update_by_book_id(self.db_client, book_id, {
            "$set": {"Copies": books_repository.get_value_of_field_by_id(self.db_client, book_id, "Copies") - 1}})

        users_repository.update_by_user_id(self.db_client, user_id, {"$set": {
            "Borrowed": borrowed_repository.check_number_of_borrowed_books(self.db_client, user_id)}})

        user_history = users_repository.get_value_of_field_by_id(self.db_client, user_id, "History")
        user_history.append(tuple(self.admin_tree.item(item, "values"))[1])
        users_repository.update_by_user_id(self.db_client, user_id, {"$set": {"History": user_history}})

        self.users_refresh()
        #refresh
        self.cancel_search()
        return False



# kopie registrace uživatele

    def users_create_user(self):
        self.user_create_window = tk.Toplevel(self.root)
        self.user_create_window.title("User creation")

        self.label_name = tk.Label(self.user_create_window, text="Name:")
        self.label_surname = tk.Label(self.user_create_window, text="Surname:")
        self.label_birthdate = tk.Label(self.user_create_window, text="Birthnumber:")
        self.label_adress = tk.Label(self.user_create_window, text="Adress:")
        self.label_reg_username = tk.Label(self.user_create_window, text="Username:")
        self.label_reg_password = tk.Label(self.user_create_window, text="Password:")

        self.entry_name = tk.Entry(self.user_create_window)
        self.entry_surname = tk.Entry(self.user_create_window)
        self.entry_birthdate = tk.Entry(self.user_create_window)
        self.entry_adress = tk.Entry(self.user_create_window)
        self.entry_reg_username = tk.Entry(self.user_create_window)
        self.entry_reg_password = tk.Entry(self.user_create_window, show="*")

        self.label_name.grid(row=0, column=0)
        self.label_surname.grid(row=1, column=0)
        self.label_birthdate.grid(row=2, column=0)
        self.label_adress.grid(row=3, column=0)
        self.label_reg_username.grid(row=4, column=0)
        self.label_reg_password.grid(row=5, column=0)

        self.entry_name.grid(row=0, column=1)
        self.entry_surname.grid(row=1, column=1)
        self.entry_birthdate.grid(row=2, column=1)
        self.entry_adress.grid(row=3, column=1)
        self.entry_reg_username.grid(row=4, column=1)
        self.entry_reg_password.grid(row=5, column=1)

        register_button = tk.Button(self.user_create_window, text="Register", command=self.register)
        register_button.grid(row=6, columnspan=2)

    def register(self):
        name = self.entry_name.get()
        surname = self.entry_surname.get()
        birthdate = self.entry_birthdate.get()
        adress = self.entry_adress.get()
        username = self.entry_reg_username.get()
        password = self.entry_reg_password.get()

        if not (len(name) >= 1) and (len(surname) >= 1) and (len(birthdate) >= 1) and (len(adress) >= 1) and (len(username) >= 1) and (len(password) >= 1):
            messagebox.showerror("Everything must be filled out", "Everything must be filled out")
            return

        users_repository.create_user_admin(self.db_client,name,surname,birthdate,adress,username,password)
        self.users_refresh()
        # Zavření okna registrace
        self.user_create_window.destroy()

#kopie editace vlastníc udajů

    def show_selected_user_info(self):
        self.selected_info_window = tk.Toplevel(self.root)
        self.selected_info_window.title("User information")

        label_name = tk.Label(self.selected_info_window, text="Name:")
        label_surname = tk.Label(self.selected_info_window, text="Surname:")
        label_birthdate = tk.Label(self.selected_info_window, text="Birthdate:")
        label_adress = tk.Label(self.selected_info_window, text="Adress:")
        label_info_username = tk.Label(self.selected_info_window, text="Username:")
        label_info_password = tk.Label(self.selected_info_window, text="Password:")

        entry_name = tk.Entry(self.selected_info_window)
        entry_surname = tk.Entry(self.selected_info_window)
        entry_birthdate = tk.Entry(self.selected_info_window)
        entry_adress = tk.Entry(self.selected_info_window)
        entry_info_username = tk.Entry(self.selected_info_window)
        entry_info_password = tk.Entry(self.selected_info_window, show="*")

        label_name.grid(row=0, column=0)
        label_surname.grid(row=1, column=0)
        label_birthdate.grid(row=2, column=0)
        label_adress.grid(row=3, column=0)
        label_info_username.grid(row=4, column=0)
        label_info_password.grid(row=5, column=0)

        entry_name.grid(row=0, column=1)
        entry_surname.grid(row=1, column=1)
        entry_birthdate.grid(row=2, column=1)
        entry_adress.grid(row=3, column=1)
        entry_info_username.grid(row=4, column=1)
        entry_info_password.grid(row=5, column=1)

        selected_items = self.users_tree.selection()
        id_of_user = 0
        # změna statusu bannování
        for item in selected_items:
            id_of_user = tuple(self.users_tree.item(item, "values"))[0]

        # Místo "" hodit co info z DB nebo tabulky (prozatím jsou tam fešné placeholdery)
        user_info = users_repository.find_document_by_id(self.db_client, id_of_user)
        entry_name.insert(0, user_info["Name"])
        entry_surname.insert(0, user_info["Surename"])
        entry_birthdate.insert(0, user_info["BirthNumber"])
        entry_adress.insert(0, user_info["Address"])
        entry_info_username.insert(0, user_info["Username"])
        # Password pole je necháno prázné

        confirm_button = tk.Button(self.selected_info_window, text="Confirm", command=lambda: self.check_changes_of_selected(
            entry_name.get(),
            entry_surname.get(),
            entry_birthdate.get(),
            entry_adress.get(),
            entry_info_username.get(),
            entry_info_password.get()
        ))
        confirm_button.grid(row=6, columnspan=2)

    def check_changes_of_selected(self, name, surname, birthdate, adress, info_username, info_password):
        selected_items = self.users_tree.selection()
        id_of_user = 0
        # změna statusu bannování
        for item in selected_items:
            id_of_user = tuple(self.users_tree.item(item, "values"))[0]
        user_info = users_repository.find_document_by_id(self.db_client, id_of_user)
        # Je tu jen hodne hodne hruby nastrel
        if any([
            name != "",
            surname != "",
            birthdate != "",
            adress != "",
            info_username != ""
        ]):
            if info_username != user_info["Username"]:
                user = self.db_client.Library.Users.find_one({"Username": info_username})
                if user is not None:
                    return "Username already exists"
            # Changes were made, show confirmation message
            confirmation_message = f"Do you want to apply changes for user {info_username}?"
            result = messagebox.askyesnocancel("Confirmation", confirmation_message)

            if result is not None:
                if result:  # Yes
                    if any([
                        name == "",
                        surname == "",
                        birthdate == "",
                        info_username == ""  # ,
                        # info_password == "",
                    ]):
                        self.show_error_message("All inputs must be filled.")
                    else:
                        if info_password == "":
                            users_repository.edit_by_user_id_no_passwd(self.db_client, id_of_user, name,
                                                                       surname, birthdate, adress, info_username)
                        else:
                            users_repository.edit_by_user_id(self.db_client, id_of_user, name, surname,
                                                             birthdate, adress, info_username, info_password)

                        print(f"User data updated for user {info_username}")
                        self.selected_info_window.destroy()
                        self.users_refresh()

                elif not result:  # No
                    self.selected_info_window.destroy()
                # else:
                # show_user_info.destroy()
        else:
            self.selected_info_window.destroy()








#Customer layout, nedodělán
#TODO: po dodělání admin layoutu zkopírovat ho a odstranit některé funkce (přidat edit profilu pro customera)


    def show_customer_layout(self):
        self.login_frame.destroy()
        customer_frame = tk.Frame(self.root, width=1220, height=280)
        customer_frame.pack()

        label = tk.Label(customer_frame, text="Welcome, Customer!")
        label.pack()

        logout_button = tk.Button(customer_frame, text="Logout", command=self.logout)
        logout_button.pack()

        search_label = tk.Label(customer_frame, text="Search Books:")
        search_label.pack()

        search_button = tk.Button(customer_frame, text="Search", command=self.customer_show_search_window)
        search_button.pack()

        cancel_search_button = tk.Button(customer_frame, text="Cancel Search/ Refresh", command=self.customer_cancel_search)
        cancel_search_button.pack()


        # Zobrazení okna s informacemi uživatele
        user_info_button = tk.Button(customer_frame, text="User info", command=self.show_user_info)
        user_info_button.pack()


        borrow_book_button = tk.Button(customer_frame, text="Borrow book", command=self.customer_borrow_book)
        borrow_book_button.pack()


        borrow_view_button = tk.Button(customer_frame, text="Borrowed books", command=self.show_borrowed_layout)
        borrow_view_button.pack()

        columns = ("Id", "Title", "Author", "Genre", "Pages", "Year", "Copies")
        self.customer_tree = ttk.Treeview(customer_frame, columns=columns, show="headings")

        for col in columns:
            self.customer_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        for col in columns:
            if col == "Id":
                self.customer_tree.column(col, stretch="no", minwidth=0, width=0)
                continue
            self.customer_tree.column(col, stretch="yes", minwidth=0, width=200)

        self.customer_tree.pack()

        #books = [("Book1", "Author1", "Genre1", 5), ("Book2", "Author2", "Genre2", 3), ("Book3", "Author3", "Genre3", 7)]
        # Plnění treeview daty z databáze
        for document in books_repository.find_all_documents(self.db_client):
            books_data = ((document["_id"], document["Title"], document["Author"], document["Genre"], document["Pages"],
                           document["Year"], document["Copies"]))
            self.customer_tree.insert("", "end", values=books_data)


    def customer_borrow_book(self):
        # Seznam vybraných řádků
        selected_items = self.customer_tree.selection()
        current_user_info = users_repository.find_document_by_id(self.db_client, currentUser["_id"])
        # kontrola počtu vypůjčených knih
        if current_user_info["Borrowed"] >= 6:
            print("too many borrowed books")
            messagebox.showerror("Too many borrowed books", "You have too many borrowed books (6 books)")
            return False
        if not current_user_info["Confirmed"]:
            print("not confirmed")
            messagebox.showerror("Not confirmed", "Your account is not confirmed")
            return False

        # vypůjčování knížky
        for item in selected_items:
            id_of_book = tuple(self.customer_tree.item(item, "values"))[0]
            # kontrola jestli ji již má vypůjčenou
            borrowed = borrowed_repository.find_document_by_ids(self.db_client, currentUser["_id"], id_of_book)
            if borrowed is not None:
                print("already borrowed")
                messagebox.showerror("Already borrowed", "You have a copie of this book already borrowed")
                return False
            if books_repository.get_value_of_field_by_id(self.db_client, id_of_book, "Copies") <= 0:
                print("not enough copies")
                messagebox.showerror("Not enough copies", "Not enough copies to borrow")
                return False
            print("borrowing")
            # vypujčování
            borrowed_repository.create_borrowed(self.db_client, currentUser["_id"], id_of_book)
            # přepis počtu kopií
            books_repository.update_by_book_id(self.db_client, id_of_book, {"$set": {
                "Copies": books_repository.get_value_of_field_by_id(self.db_client, id_of_book, "Copies") - 1}})
            # přepis počtu vypůjčených knih u usera
            users_repository.update_by_user_id(self.db_client, currentUser["_id"], {"$set": {
                "Borrowed": borrowed_repository.check_number_of_borrowed_books(self.db_client, currentUser["_id"])}})
            # načtení historie
            user_history = users_repository.get_value_of_field_by_id(self.db_client, currentUser["_id"], "History")
            # zapsání do historie lokálně
            user_history.append(tuple(self.customer_tree.item(item, "values"))[1])
            print(user_history)
            # nahrání historie na DB
            users_repository.update_by_user_id(self.db_client, currentUser["_id"], {"$set": {"History": user_history}})
        # refresh
        self.customer_cancel_search()

    def customer_show_search_window(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Books")

        title_label = tk.Label(search_window, text="Title:")
        title_label.grid(row=0, column=0, padx=5, pady=5)
        title_entry = tk.Entry(search_window)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        author_label = tk.Label(search_window, text="Author:")
        author_label.grid(row=1, column=0, padx=5, pady=5)
        author_entry = tk.Entry(search_window)
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        genre_label = tk.Label(search_window, text="Genre:")
        genre_label.grid(row=2, column=0, padx=5, pady=5)
        genre_entry = tk.Entry(search_window)
        genre_entry.grid(row=2, column=1, padx=5, pady=5)

        # Tlačítko confirm vezme inputy a  zavolá funkci search_books
        confirm_button = tk.Button(search_window, text="Confirm", command=lambda: self.customer_search_books(
            title_entry.get(), author_entry.get(), genre_entry.get(), search_window))
        confirm_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Funkce pro hledání knihy, kontroluje minimální délku inputů
        # TODO: ošetřit velikost vstupu

    def customer_search_books(self, title, author, genre, search_window):
        # Kontrola jestli jsou v inputech alespoň 3 znaky nebo jsou null
        if not (len(title) >= 3 or len(title) == 0) and (len(author) >= 3 or len(author) == 0) and (
                len(genre) >= 3 or len(genre) == 0):
            messagebox.showerror("Filed needs to be 3 or more", "Filed needs to be 3 or more characters")
            return
        # Kontrola jestli všechny inputy nejsou null
        if (len(title) == 0 and len(author) == 0 and len(genre) == 0):
            messagebox.showerror("No valid input", "No valid inputs for search")
            return

        # Clear existing items in the treeview
        self.customer_tree.delete(*self.customer_tree.get_children())

        # Filter books based on search criteria
        searchResult = books_repository.search_documents(self.db_client, title, author, genre)
        # searchResult = books_repository.find_documents(self.db_client, {"$and": queries})
        for book in searchResult:
            if (book == None):
                return
            book_data = (
            (book["_id"], book["Title"], book["Author"], book["Genre"], book["Pages"], book["Year"], book["Copies"]))
            self.customer_tree.insert("", "end", values=book_data)

        # Close the search window
        search_window.destroy()

        # Funkce cancel search opět zobrazí vše ve výběru

    def customer_cancel_search(self):
        # Clear search criteria and display all books
        self.customer_tree.delete(*self.customer_tree.get_children())
        for document in books_repository.find_all_documents(self.db_client):
            books_data = ((document["_id"], document["Title"], document["Author"], document["Genre"], document["Pages"],
                           document["Year"], document["Copies"]))
            self.customer_tree.insert("", "end", values=books_data)







    def logout(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.resizable(False, False)
        self.root.attributes("-toolwindow", 1)
        self.center_window()
        self.create_login_frame()
        self.root.mainloop()
