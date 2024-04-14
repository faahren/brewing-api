from models.ping import Ping
import datetime

class PingFactory():

    def create_ping(self, json_body):
        #Add all sanity checks
        data = json_body
        ping = Ping()
        ping.datetime = datetime.datetime.now()
        ping.device_name = data["name"]
        ping.device_id = data["ID"]
        ping.device_token = data["token"]
        ping.device_type = "ispindel"
        ping.angle = data["angle"]
        ping.temperature = data["temperature"]
        ping.temp_units = data["temp_units"]
        ping.battery = data["battery"]
        ping.gravity = data["gravity"]
        ping.interval = data["interval"]
        ping.RSSI = data["RSSI"]
        return ping