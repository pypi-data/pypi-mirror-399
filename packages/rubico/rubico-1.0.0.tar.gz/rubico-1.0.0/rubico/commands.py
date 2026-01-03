class Command:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    def check(self, message):
        text = message.get("text", "")
        return text.startswith(f"/{self.name}")
