import os
import time
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreService():
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            '/tmp/keys/ADC.json', scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.db = firestore.Client(project=os.getenv("project_id"), credentials=credentials, database=os.getenv("database_id"))
    
    def insert(self, collection, data):
        doc_ref = self.db.collection(collection).document(str(time.time()))
        doc_ref.set(data)
        return True