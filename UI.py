import base64
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

from Repositories.BooksRepository import create_book, find_all_documents
from Repositories import ConnectToDatabase as db

class App:
    books = [("Book1", "Author1", "Genre1", 5), ("Book2", "Author2", "Genre2", 3), ("Book3", "Author3", "Genre3", 7)]
    db_client = db.connect_to_mongodb()

    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.resizable(False, False)
        self.root.attributes("-toolwindow", 1)
        self.center_window()
        self.create_login_frame()        
        self.image_path = None
        self.image_references = {}

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        #x = (screen_width - self.root.winfo_reqwidth()) // 2
        #y = (screen_height - self.root.winfo_reqheight()) // 2
        x = (screen_width//2) -401
        y = (screen_height//2) -140
        self.root.geometry("+{}+{}".format(x, y))
    
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

    #Login funkce
    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        #Placeholder pro login, je třeba implementovat
        #TODO: implementovat ověřování loginů oproti databázi
        if username == "admin" and password == "admin":
            self.show_admin_layout()
        elif username == "customer" and password == "customer":
            self.show_customer_layout()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

#Konec inicializace UI a loginu
######################################################################################################################
#Admin layout a funkce s ním spojené
#TODO: přidat button zobrazující list čekajících úprav profilu a nových registrací, přidat dvojklikem možnost rozbalení knihy a upravení jejich parametrů
    
    #Admin layout
    def show_admin_layout(self):
        self.login_frame.destroy()
        admin_frame = tk.Frame(self.root, width=1405, height=280)
        admin_frame.pack()

        logout_button = tk.Button(admin_frame, text="Logout", command=self.logout)

        columns = ("Title", "Author", "Genre", "Pages", "Year", "Copies", "Image")
        self.sort_order = {col: True for col in columns}

        self.admin_tree = ttk.Treeview(admin_frame, columns=columns, selectmode='browse', show="headings")

        for col in columns:
            self.admin_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        self.admin_tree.place(x=0, y=40 + 15)

        logout_button.place(x=(self.admin_tree.winfo_reqwidth() - logout_button.winfo_reqwidth()), y=0)

        all_documents = find_all_documents(self.db_client)

        for book in all_documents:
            title = book["Title"]
            author = book["Author"]
            genre = book["Genre"]
            pages = book["Pages"]
            year = book["Year"]
            copies = book["Copies"]
            picture_binary = book.get("Picture")

            # Convert binary image data to Tkinter PhotoImage using Pillow
            image_label = "Image Preview"
            if picture_binary:
                img = Image.open(BytesIO(picture_binary))
                img.thumbnail((50, 50))  # Adjust size as needed
                tk_img = ImageTk.PhotoImage(img)

                # Insert the data into the treeview
                book_data = (title, author, genre, pages, year, copies, tk_img)
                self.admin_tree.insert("", "end", values=book_data)

        delete_button = tk.Button(admin_frame, text="Delete", command=self.delete_selected, width=6)
        delete_button.place(x=(self.admin_tree.winfo_reqwidth() - logout_button.winfo_reqwidth()), y=logout_button.winfo_reqheight())

        self.admin_tree.bind("<Delete>", lambda event: self.delete_selected())

        add_button = tk.Button(admin_frame, text="Add Book", command=self.show_add_window)
        add_button.place(x=(self.admin_tree.winfo_reqwidth() - delete_button.winfo_reqwidth() - add_button.winfo_reqwidth() - 5), y=logout_button.winfo_reqheight())

        search_button = tk.Button(admin_frame, text="Search", command=self.show_search_window)
        search_button.place(x=(self.admin_tree.winfo_reqwidth() - delete_button.winfo_reqwidth() - add_button.winfo_reqwidth() - 5), y=0)

        cancel_search_button = tk.Button(admin_frame, text="Cancel Search", command=self.cancel_search)
        cancel_search_button.place(x=(self.admin_tree.winfo_reqwidth() - logout_button.winfo_reqwidth() - add_button.winfo_reqwidth() - cancel_search_button.winfo_reqwidth() - 15), y=0)

#-------------------------------------------------------------------------------------------------------------------------
#Konec admin layoutu, níže jsou funkce pro admin layout
#-------------------------------------------------------------------------------------------------------------------------

    #Vymaže vybranou knihu z treeview
    #TODO: implementovat mazání z databáze
    def delete_selected(self):
        #Seznam vybraných řádků
        selected_items = self.admin_tree.selection()
        #Mazání jednotlivých itemů
        for item in selected_items:
            self.admin_tree.delete(item)
        #Aktualizování placeholderu App.books 
        App.books = []
        for item in self.admin_tree.get_children():
            book_data = tuple(self.admin_tree.item(item, "values"))
            App.books.append(book_data)


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
    #TODO: udělat select na straně databáze a natáhnout to sem
    def search_books(self, title, author, genre, search_window):
        #Kontrola jestli jsou v inputech alespoň 3 znaky nebo jsou null
        if not (len(title) >= 3 or len(title)==0) and (len(author) >= 3 or len(author)==0) and (len(genre) >= 3 or len(genre)==0):
            self.show_error_message("Each input has to have atleast 3 characters or be empty.")
            return
        #Kontrola jestli všechny inputy nejsou null
        if (len(title)==0 and len(author)==0 and len(genre)==0):
            self.show_error_message("No valid inputs for search.")
            return
        
        #Clear existing items in the treeview
        self.admin_tree.delete(*self.admin_tree.get_children())

        #Filter books based on search criteria
        for book in App.books:
            if (
                (not title or title.lower() in book[0].lower()) and
                (not author or author.lower() in book[1].lower()) and
                (not genre or genre.lower() in book[2].lower())
            ):
                self.admin_tree.insert("", "end", values=book)

        #Close the search window
        search_window.destroy()

    #Funkce cancel search opět zobrazí vše ve výběru
    #TODO: zde natáhnout opět select všeho co chcem zobrazit bez podmínek
    def cancel_search(self):
        #Clear search criteria and display all books
        self.admin_tree.delete(*self.admin_tree.get_children())
        for book in App.books:
            self.admin_tree.insert("", "end", values=book)

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
                self.admin_tree.insert("", "end", values=(title, author, genre, int(copies)))

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


#Konec admin layoutu a funkcí
######################################################################################################################
#Customer layout, nedodělán
#TODO: po dodělání admin layoutu zkopírovat ho a odstranit některé funkce (přidat edit profilu pro customera)

    def show_customer_layout(self):
        self.login_frame.destroy()
        customer_frame = tk.Frame(self.root)
        customer_frame.pack()
        label = tk.Label(customer_frame, text="Welcome, Customer!")
        label.pack()
        logout_button = tk.Button(customer_frame, text="Logout", command=self.logout)
        logout_button.pack()

        search_label = tk.Label(customer_frame, text="Search Books:")
        search_label.pack()

        search_entry = tk.Entry(customer_frame)
        search_entry.pack()

        search_button = tk.Button(customer_frame, text="Search", command=lambda: self.search_books(search_entry.get()))
        search_button.pack()

        columns = ("Title", "Author", "Genre", "Copies", "Action")
        self.customer_tree = ttk.Treeview(customer_frame, columns=columns, show="headings")

        for col in columns:
            self.customer_tree.heading(col, text=col)

        self.customer_tree.pack()

        books = [("Book1", "Author1", "Genre1", 5), ("Book2", "Author2", "Genre2", 3), ("Book3", "Author3", "Genre3", 7)]

        for book in books:
            book_data = book
            delete_button = tk.Button(customer_frame, text="Delete", command=lambda b=book_data: self.delete_book(b))
            self.customer_tree.insert("", "end", values=book_data + (delete_button,))
        

    def logout(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.resizable(False, False)
        self.root.attributes("-toolwindow", 1)
        self.center_window()
        self.create_login_frame()
        self.root.mainloop()
