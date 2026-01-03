from .context import Message

class Dispatcher:
    def __init__(self, client):
        self.client = client
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def dispatch(self, update):
        message = Message(update, self.client)
        for handler in self.handlers:
            if handler.check(message):
                handler.callback(message)
