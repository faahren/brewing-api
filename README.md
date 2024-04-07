# Brewing API

Host a iSpindel server on Google Cloud Platform to own your brewing data and forward it to an external system if you want

Steps to use it:

* Create a GCP Project and enable Cloud Run and Firestore APIs
* Create a service account that has Firestore User role and paste the JSON Key in config/sa.json
* Create a .env file in /config based on given template and replace with your info
* Deploy the service with `bash ./deploy.sh/`


