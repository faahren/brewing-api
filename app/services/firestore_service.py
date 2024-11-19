import os
import time
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreService():
    def __init__(self):
        try:
            self.db = firestore.Client(project=os.getenv("project_id"), database=os.getenv("firestore_database_id"))
        except Exception as e:
            print("There was an error with the FirestoreService")
    
    def insert(self, collection, data):
        doc_ref = self.db.collection(collection).document(str(time.time()))
        doc_ref.set(data)
        return True
    
    def get_results_by(self, collection, field, value):
        try:
            print(collection, field, value) 
            return self.get_list_as_dict(self.db.collection(collection).where(field, "==", value).stream())
        except Exception as e:
            print("There was an error with the get_results_by method")
    
    def get_list_as_dict(self, results):
        return [result.to_dict() for result in results]
    
    def get_collection(self, collection):
        try:
            return self.db.collection(collection)
        except Exception as e:
            print("There was an error with the get_collection method")
    
    def get_all_results(self, collection):
        try:
            return self.get_list_as_dict(self.db.collection(collection).stream())
        except Exception as e:
            print("There was an error with the get_all_results method")
    
    def get_one_by(self, collection, field, value):
        try:
            results = self.db.collection(collection).where(field, "==", value).stream()
            print(results)
            for result in results:
                return result.to_dict()
        except Exception as e:
            print("There was an error with the get_one_by method")