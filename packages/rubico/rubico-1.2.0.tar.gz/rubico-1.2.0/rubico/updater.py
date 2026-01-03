class Updater:
    def __init__(self, client):
        self.client = client
        self.offset = 0

    def fetch(self):
        while True:
            updates = self.client.call("getUpdates", {
                "offset": self.offset,
                "timeout": 20
            })
            for upd in updates:
                self.offset = upd["update_id"] + 1
                yield upd
