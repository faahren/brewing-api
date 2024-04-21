from models.repository import Repository

class PingRepository(Repository):
    def __init__(self):
        super().__init__()
        self.table = "pings"


    def get_last_metrics_by_deviceid(self, device_id):
        query = f"""
with import as (
    SELECT 
    *,
    FIRST_VALUE(gravity) OVER (PARTITION BY device_id order by datetime ASC) as di
FROM {self.db.dataset_id}.{self.table}
WHERE device_id = '{device_id}'
    ORDER BY datetime DESC
    LIMIT 1
)
select
    *,
    (0.13*((di-1) - (gravity-1)) * 1000) as alcool
from import
        """
        rows = self.db.get_query_results(query)
        for row in rows:
            return dict(row.items())
        
    def get_metrics_history(self):
        query = f"""
with import as (
    SELECT 
    FORMAT_DATETIME("%Y-%m-%d %T", datetime) as date_formatted,
    *,
    FIRST_VALUE(gravity) OVER (PARTITION BY device_id order by datetime ASC) as di
FROM {self.db.dataset_id}.{self.table}
    ORDER BY datetime DESC
)
select
    *,
    (0.13*((di-1) - (gravity-1)) * 1000) as alcool
from import
"""
        rows = self.db.get_query_results(query)
        return [dict(row.items()) for row in rows]
        
