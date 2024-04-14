import os
from google.cloud import bigquery
from google.oauth2 import service_account

class BigqueryService():
    def __init__(self):
        self.client = bigquery.Client(project=os.getenv('PROJECT_ID'))
        self.dataset_id = os.getenv('DATASET_ID')
    
    def insert(self, table_id, data):
        
        table = self.client.get_table(f"{self.dataset_id}.{table_id}")
        rows_to_insert = [vars(data)]
        print(rows_to_insert)        
        errors = self.client.insert_rows(table, rows_to_insert)
        if errors == []:
            return True
        else:
            return False