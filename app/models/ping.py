from models.entity import Entity
from datetime import datetime

class Ping(Entity):
    datetime: datetime
    device_name: str
    device_id: int
    device_token: str
    device_type: str
    angle: float
    temperature: float
    temp_units: str
    battery: float
    gravity: float
    interval: int
    RSSI: int