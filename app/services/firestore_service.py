import os
import time
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreService():
    def __init__(self):
        self.db = firestore.Client(project=os.getenv("project_id"), database=os.getenv("firestore_database_id"))
    
    def insert(self, collection, data):
        doc_ref = self.db.collection(collection).document(str(time.time()))
        doc_ref.set(data)
        return True
    
    def get_results_by(self, collection, field, value):
        print(collection, field, value)
        return self.get_list_as_dict(self.db.collection(collection).where(field, "==", value).stream())
    
    def get_list_as_dict(self, results):
        return [result.to_dict() for result in results]
    
    def get_collection(self, collection):
        return self.db.collection(collection)
    
    def get_all_results(self, collection):
        return self.get_list_as_dict(self.db.collection(collection).stream())
    
    def get_one_by(self, collection, field, value):
        results = self.db.collection(collection).where(field, "==", value).stream()
        print(results)
        for result in results:
            return result.to_dict()