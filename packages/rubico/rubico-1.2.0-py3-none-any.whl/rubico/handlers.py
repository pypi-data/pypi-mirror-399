class MessageHandler:
    def __init__(self, callback):
        self.callback = callback

    def check(self, message):
        return True
