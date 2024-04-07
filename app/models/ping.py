from models.entity import Entity
class Ping(Entity):
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