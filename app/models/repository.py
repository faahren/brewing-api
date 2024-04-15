from services.bigquery_service import BigqueryService

class Repository():
    def __init__(self):
        self.db = BigqueryService()