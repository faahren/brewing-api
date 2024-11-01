from services.firestore_service import FirestoreService

class FireRepository():
    def __init__(self, collection):
        self.db = FirestoreService()
        self.collection = collection

    def get_results_by(self, field, value):
        print(self.collection)
        
        return self.db.get_results_by(self.collection, field, value)
    
    def get_all_results(self):
        return self.db.get_all_results(self.collection)