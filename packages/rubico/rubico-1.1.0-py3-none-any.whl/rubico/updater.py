class UpdateManager:
    def __init__(self, client):
        self.client = client
        self.offset = 0

    def fetch(self):
        res = self.client.call("getUpdates", {"offset": self.offset})
        messages = []
        for upd in res.get("result", []):
            self.offset = upd["update_id"] + 1
            if "message" in upd:
                messages.append(upd["message"])
        return messages
