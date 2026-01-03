class Command:
    def __init__(self, name):
        self.name = name

    def check(self, message):
        return message.text.startswith(f"/{self.name}")
