import requests

class RubicoClient:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.rubika.ir/bot{self.token}/"

    def call(self, method, data):
        url = self.base_url + method
        response = requests.post(url, json=data)
        return response.json()
