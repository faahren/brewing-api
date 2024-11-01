import requests
import os

class ForwardService:
    def forward(self, request, forward_url):

        try:
            # Copier les headers de la requête originale
            headers = {key: value for (key, value) in request.headers if key != 'Host'}
            
            # Faire suivre la requête avec la même méthode et le même body
            response = requests.request(
                method=request.method,
                url=forward_url,
                headers=headers,
                json=request.get_json(silent=True)
            )
            
            return response.status_code
            
        except requests.exceptions.RequestException as e:
            print(f"Error forwarding request: {str(e)}")
            return None
