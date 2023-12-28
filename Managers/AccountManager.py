import bcrypt
from Repositories import UsersRepository as users_repository


def verify_password(db_client, user_name, entered_password):
    document = users_repository.find_document(db_client, {"UserName": user_name})
    if document is not None:
        return bcrypt.checkpw(entered_password.encode(), document["Password"])
    else:
        return False


def change_password(db_client, user_name, current_password, new_password):
    # Zkontrolujeme, zda uživatel existuje v databázi
    document = users_repository.find_document(db_client, {"UserName": user_name})
    if document is not None:
        hashed_current_password = document["Password"]
        if bcrypt.checkpw(current_password.encode(), hashed_current_password):
            hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            document["Password"] = hashed_new_password
            users_repository.update(db_client, {"UserName": user_name}, document)
            return True
        else:
            return False
    else:
        return False
