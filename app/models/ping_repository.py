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
        
    def get_metrics_history(self, date_start=None, date_end=None):
        where_clause = "where "
        if date_start:
            where_clause += f"FORMAT_DATETIME('%Y-%m-%d', datetime) >= '{date_start}'"
        if date_end:
            if date_start:
                where_clause += " and "
            where_clause += f"FORMAT_DATETIME('%Y-%m-%d', datetime) <= '{date_end}'"
        query = f"""
with src as (select * from {self.db.dataset_id}.{self.table} {where_clause})
,brewings as (select * from brewing.brewings)
,joined as (
  select src.*
  ,brewings.date_start as brewing_date_start
  ,brewings.date_end as brewing_date_end
  ,brewings.brewing_id
  ,brewings.name as brewing_name
  from src join brewings on DATE(datetime) BETWEEN date_start and date_end and src.device_id = CAST(brewings.device_id as STRING)
)
,calc as (
    SELECT 
    DATETIME(TIMESTAMP(datetime), "America/Toronto") as datetime_est,
    *,
    FIRST_VALUE(gravity) OVER (PARTITION BY brewing_id order by datetime ASC) as di
FROM joined
    ORDER BY datetime DESC
)
select
    *,
    FORMAT_DATETIME("%Y-%m-%d %T", datetime_est) as date_formatted,
    (0.13*((di-1) - (gravity-1)) * 1000) as alcool
from calc
"""
        rows = self.db.get_query_results(query)
        return [dict(row.items()) for row in rows]
    
    def get_metrics_increments(self, date_start= None, date_end= None):
        where_clause = "where "
        if date_start:
            where_clause += f"FORMAT_DATETIME('%Y-%m-%d', datetime) >= '{date_start}'"
        if date_end:
            if date_start:
                where_clause += " and "
            where_clause += f"FORMAT_DATETIME('%Y-%m-%d', datetime) <= '{date_end}'"
        query = f"""
with src as (select * from {self.db.dataset_id}.{self.table} {where_clause})
,brewings as (select * from brewing.brewings)
,joined as (
  select src.*
  ,brewings.date_start as brewing_date_start
  ,brewings.date_end as brewing_date_end
  ,brewings.brewing_id
  ,brewings.name as brewing_name
  from src join brewings on DATE(datetime) BETWEEN date_start and date_end and src.device_id = CAST(brewings.device_id as STRING)
)
,calc as (
    SELECT 
    DATETIME(TIMESTAMP(datetime), "America/Toronto") as datetime_est,
    *,
    FIRST_VALUE(gravity) OVER (PARTITION BY brewing_id order by datetime ASC) as di
FROM joined
    ORDER BY datetime DESC
),
calculations as (
    select
        *,
        FORMAT_DATETIME("%Y-%m-%d %T", datetime_est) as date_formatted,
        (0.13*((di-1) - (gravity-1)) * 1000) as alcool,
        FIRST_VALUE(datetime) OVER (PARTITION BY brewing_id ORDER BY datetime ASC) datetime_start
    from calc order by datetime desc
),
aggregations as (
    select 
    DATETIME_TRUNC(datetime_est, HOUR) as date,
    DATETIME_DIFF(datetime, datetime_start, HOUR) as datetime_plus,
    device_id,
    brewing_name,
    brewing_id,
    brewing_date_start,
    brewing_date_end,
    di as initial_density,
    MAX(alcool) alcool,
    MAX(gravity) density
    from calculations
    group by ALL
),
increment as (
    select 
    *,
    alcool - LAG(alcool) OVER (PARTITION BY brewing_id ORDER BY date ASC) as alcool_increment,
    density - LAG(density) OVER (PARTITION BY brewing_id ORDER BY date ASC) as density_increment
     from aggregations
)
select * from increment order by date asc 
"""
        rows = self.db.get_query_results(query)
        return [dict(row.items()) for row in rows]
    
