import requests

class RubicoClient:
    def __init__(self, token, timeout=10):
        self.token = token
        self.base_url = f"https://api.rubika.ir/bot{token}/"
        self.timeout = timeout

    def call(self, method, data):
        url = self.base_url + method
        r = requests.post(url, json=data, timeout=self.timeout)
        return r.json()
