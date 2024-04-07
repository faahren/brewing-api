from google.oauth2 import service_account
from google.cloud import firestore
import os
import time
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests

load_dotenv()


app = Flask(__name__)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    credentials = service_account.Credentials.from_service_account_file(
        'sa.json', scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    db = firestore.Client(project=os.getenv("PROJECT_ID"), credentials=credentials, database=os.getenv("DATABASE_ID"))
    doc_ref = db.collection("pings").document(str(time.time()))
    doc_ref.set({"args": request.args.to_dict() , "headers": dict(request.headers), "remote_addr": request.remote_addr, "body": request.data.decode("utf-8"), "url": request.url, "method": request.method })

    forward_url = os.getenv("FORWARD_URL")
    if (forward_url is None):
        return jsonify({"message": "ok"})
    
    res = requests.request(
        method          = request.method,
        url             = forward_url,
        headers         = {k:v for k,v in request.headers if k.lower() != 'host'},
        data            = request.get_data(),
        cookies         = request.cookies,
        allow_redirects = False,
    )

    return jsonify({"message": "ok"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))