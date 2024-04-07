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

    fs_service = FirestoreService()
    fs_service.insert("pings", {"args": request.args.to_dict() , "headers": dict(request.headers), "remote_addr": request.remote_addr, "body": ping.toJSON(), "url": request.url, "method": request.method })
    
    ForwardService().forward(request)

    return jsonify({"message": "ok"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))