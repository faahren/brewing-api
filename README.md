# Brewing API

Host a iSpindel server on Google Cloud Platform to own your brewing data and forward it to an external system if you want

Steps to use it:

* Create a GCP Project:
* Fork the repo
* Install Cloud build github App on the repo
* Generate a Github token that has: read:enterprise, read:org, read:user, repo
* Create a terraform.tfvars file based on terraform.tfvars.template and add it to your infrastructure/ folder 
* Create a .env file in /config based on given template and replace with your info
* Deploy the service terraform apply



