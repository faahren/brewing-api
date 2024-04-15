from flask import Flask, jsonify, request
from dotenv import load_dotenv

import os

from services.ping_factory import PingFactory
from services.bigquery_service import BigqueryService
from services.forward_service import ForwardService

from models.ping_repository import PingRepository

load_dotenv()
app = Flask(__name__)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    ping = PingFactory().create_ping(request.json)


    bq_service = BigqueryService()
    bq_service.insert("pings", ping)

    ForwardService().forward(request)

    return jsonify({"message": "ok"})

@app.route('/metrics/<device_id>', methods=['GET'])
def metrics(device_id):
    
    metrics = PingRepository().get_last_metrics_by_deviceid(device_id)
    return jsonify(metrics)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

