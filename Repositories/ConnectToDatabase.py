from pymongo.mongo_client import MongoClient


def connect_to_mongodb():
    uri = "mongodb+srv://admin:admin@atlascluster.kou54i6.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client

    except Exception as e:
        print("FAIL")
        print(e)
        return None
