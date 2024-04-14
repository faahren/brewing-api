from flask import Flask, jsonify, request
from dotenv import load_dotenv

import os

from services.ping_factory import PingFactory
from services.firestore_service import FirestoreService
from services.bigquery_service import BigqueryService
from services.forward_service import ForwardService

load_dotenv()
app = Flask(__name__)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    ping = PingFactory().create_ping(request.json)


    bq_service = BigqueryService()
    bq_service.insert("pings", ping)

    ForwardService().forward(request)

    return jsonify({"message": "ok"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))