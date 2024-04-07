import os
import requests

class ForwardService():
    def __init__(self):
        self.forward_url = os.getenv("FORWARD_URL")

    def forward(self, request):
        if (self is None):
            return None
        
    
        res = requests.request(
            method          = request.method,
            url             = self.forward_url,
            headers         = {k:v for k,v in request.headers if k.lower() != 'host'},
            data            = request.get_data(),
            cookies         = request.cookies,
            allow_redirects = False,
        )