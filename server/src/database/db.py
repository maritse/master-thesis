from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoDBHandler:
    def __init__(self, database_url, port, database_name):
        self.client = MongoClient(database_url)
        self.database = self.client[database_name]
        self.port = port

    def check_connection(self, timeout=3):
        try:
            client = MongoClient(self.database_url, self.port, serverSelectionTimeoutMS=timeout)
            client.close()
            return True
        except ConnectionFailure:
            return False

    def insert_document(self, collection_name, document):
        collection = self.database[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id

    def find_documents(self, collection_name, query=None):
        collection = self.database[collection_name]
        if query:
            return collection.find(query)
        else:
            return collection.find()

    def find_document_by_id(self, collection_name, document_id):
        collection = self.database[collection_name]
        return collection.find_one({"_id": document_id})

    def update_document(self, collection_name, document_id, updated_data):
        collection = self.database[collection_name]
        result = collection.update_one({"_id": document_id}, {"$set": updated_data})
        return result.modified_count

    def delete_document(self, collection_name, document_id):
        collection = self.database[collection_name]
        result = collection.delete_one({"_id": document_id})
        return result.deleted_count
