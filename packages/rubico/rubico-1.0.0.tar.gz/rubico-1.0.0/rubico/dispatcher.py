class Dispatcher:
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def dispatch(self, message):
        for handler in self.handlers:
            if handler.filter.check(message):
                handler.callback(message)
