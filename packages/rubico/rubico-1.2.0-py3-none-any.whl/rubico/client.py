import requests

BASE_URL = "https://botapi.rubika.ir/v1"

class RubikaClient:
    def __init__(self, token, timeout=20):
        self.token = token
        self.timeout = timeout
        self.base_url = f"{BASE_URL}/{token}"

    def call(self, method, data=None):
        url = f"{self.base_url}/{method}"
        r = requests.post(url, json=data or {}, timeout=self.timeout)
        r.raise_for_status()
        res = r.json()
        if not res.get("ok"):
            raise Exception(res)
        return res["result"]
