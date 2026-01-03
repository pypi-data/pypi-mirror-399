class Command:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    def check(self, msg):
        return msg.get("text", "").startswith(f"/{self.name}")
