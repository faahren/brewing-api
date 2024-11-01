from google.cloud import firestore
from models.firerepository import FireRepository

class DeviceRepository(FireRepository):
    def __init__(self):
        super().__init__("devices")
    

    def get_device_by_id(self, device_id):
        device = self.get_one_by("device_id", device_id)
        if device is not None:
            return device
        return None 