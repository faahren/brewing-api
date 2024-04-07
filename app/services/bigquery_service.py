import os
from google.cloud import bigquery
from google.oauth2 import service_account

class BigqueryService():
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            'sa.json', scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.client = bigquery.Client(project=os.getenv('PROJECT_ID'), credentials=credentials)
        self.dataset_id = os.getenv('DATASET_ID')
    
    def insert(self, table_id, data):
        table = self.client.get_table(f"{self.dataset_id}.{table_id}")
        rows_to_insert = [data]
        errors = self.client.insert_rows(table, rows_to_insert)
        if errors == []:
            return True
        else:
            return False