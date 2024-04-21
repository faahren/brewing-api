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
    DATETIME(TIMESTAMP(datetime), "America/Toronto") as datetime_est,
    FIRST_VALUE(gravity) OVER (PARTITION BY device_id order by datetime ASC) as di
FROM {self.db.dataset_id}.{self.table}
WHERE device_id = '{device_id}'
    ORDER BY datetime DESC
    LIMIT 1
)
select
    *,
    FORMAT_DATETIME("%Y-%m-%d %T", datetime_est) as date_formatted,
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
    DATETIME(TIMESTAMP(datetime), "America/Toronto") as datetime_est,
    *,
    FIRST_VALUE(gravity) OVER (PARTITION BY device_id order by datetime ASC) as di
FROM {self.db.dataset_id}.{self.table}
    ORDER BY datetime DESC
)
select
    *,
    FORMAT_DATETIME("%Y-%m-%d %T", datetime_est) as date_formatted,
    (0.13*((di-1) - (gravity-1)) * 1000) as alcool
from import
"""
        rows = self.db.get_query_results(query)
        return [dict(row.items()) for row in rows]
    
    def get_metrics_increments(self):
        query = f"""

with import as (
    SELECT 
    DATETIME(TIMESTAMP(datetime), "America/Toronto") as datetime_est,
    *,
    FIRST_VALUE(gravity) OVER (PARTITION BY device_id order by datetime ASC) as di
FROM brewing.pings
    ORDER BY datetime DESC
),
calculations as (
    select
        *,
        FORMAT_DATETIME("%Y-%m-%d %T", datetime_est) as date_formatted,
        (0.13*((di-1) - (gravity-1)) * 1000) as alcool
    from import order by datetime desc
),
aggregations as (
    select 
    DATE(datetime_est) date,
    device_id,
    MAX(alcool) alcool,
    MAX(gravity) density
    from calculations
    group by 1,2
),
increment as (
    select 
    *,
    alcool - LAG(alcool) OVER (PARTITION BY device_id ORDER BY date ASC) as alcool_increment,
    density - LAG(density) OVER (PARTITION BY device_id ORDER BY date ASC) as density_increment
     from aggregations
)
select * from increment
"""
        rows = self.db.get_query_results(query)
        return [dict(row.items()) for row in rows]
        
