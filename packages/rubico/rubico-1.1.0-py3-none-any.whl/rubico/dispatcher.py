class Dispatcher:
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def dispatch(self, message):
        for h in self.handlers:
            if h.filter.check(message):
                h.callback(message)
