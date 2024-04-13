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
* The install will fail at some point - Open cloud build https://console.cloud.google.com/cloud-build/, get in your region and run a build of the created trigger
* Once the build is validated, re-run terraform apply
* Create your domain mapping manually in https://console.cloud.google.com/run/domains. Terraform is still buggy as the feature is not yet GA in GCP



