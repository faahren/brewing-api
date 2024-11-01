from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime
import os

from services.ping_factory import PingFactory
from services.bigquery_service import BigqueryService
from services.forward_service import ForwardService

from models.ping_repository import PingRepository
from models.brewings_repository import BrewingsRepository
load_dotenv()
app = Flask(__name__)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    ping = PingFactory().create_ping(request.json)


    bq_service = BigqueryService()
    bq_service.insert("pings", ping)

    ForwardService().forward(request)

    return jsonify({"message": "ok"})

@app.route('/metrics/brewing/<brewing_id>', methods=['GET'])
def metrics(brewing_id):
    brewing = BrewingsRepository().get_brewing_by_id(brewing_id)
    if brewing is None:
        return jsonify({"error": "No brewing found"}), 404
    metrics = PingRepository().get_metrics_history(brewing['date_start'], brewing['date_end'])
    return jsonify(metrics)

@app.route('/metrics/device/<device_id>', methods=['GET'])
def metrics_device(device_id):
    brewing = BrewingsRepository().get_last_brewing(device_id)
    if brewing is None:
        return jsonify({"error": "No brewing found"}), 404
    metrics = PingRepository().get_metrics_history(brewing['date_start'], brewing['date_end'])
    return jsonify(metrics)

@app.route('/brewings/<device_id>/all', methods=['GET'])
def brewings_all(device_id):
    brewings = BrewingsRepository().get_all_brewings(device_id)
    return jsonify(brewings)


@app.route('/brewings/<device_id>/current', methods=['GET'])
def brewings_current(device_id):
    brewing = BrewingsRepository().get_brewing_by_date(device_id, datetime.now().date())
    return jsonify(brewing)

@app.route('/brewings/<device_id>/last', methods=['GET'])
def brewings_last(device_id):
    brewing = BrewingsRepository().get_last_brewing(device_id)
    return jsonify(brewing)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

