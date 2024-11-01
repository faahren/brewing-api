from models.firerepository import FireRepository
from datetime import datetime

class BrewingsRepository(FireRepository):
    def __init__(self):
        super().__init__("brewings")
    
    def get_brewing_by_date(self, device_id, date):
        date = date.strftime("%Y-%m-%d")
        results = self.db.get_collection("brewings").where("device_id", "==", device_id).where("date_start", "<=", date).where("date_end", ">=", date).stream()
        for result in results:
            return result.to_dict()
        return None
    
    def get_last_brewing(self, device_id):
        results = self.get_results_by("device_id", device_id)
        
        # Exclude future brewings
        results = [x for x in results if x['date_start'] <= datetime.now().date().strftime("%Y-%m-%d")]
        results.sort(key=lambda x: x['date_start'], reverse=True)

        return results[0]
    
    def get_all_brewings_by_device_id(self, device_id):
        results = self.get_results_by("device_id", device_id)
        return results
    
    def get_all_brewings(self):
        results = self.get_all_results()
        return results