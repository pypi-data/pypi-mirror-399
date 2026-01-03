class UpdateManager:
    def __init__(self, client):
        self.client = client
        self.offset = 0

    def fetch(self):
        updates = self.client.call("getUpdates", {"offset": self.offset})
        messages = []
        for u in updates.get("result", []):
            messages.append(u["message"])
            self.offset = u["update_id"] + 1
        return messages
