from .client import RubikaClient
from .updater import Updater
from .dispatcher import Dispatcher
from .handlers import MessageHandler

class Bot:
    def __init__(self, token):
        self.client = RubikaClient(token)
        self.updater = Updater(self.client)
        self.dispatcher = Dispatcher(self.client)

    def on_message(self):
        def decorator(func):
            self.dispatcher.add_handler(MessageHandler(func))
            return func
        return decorator

    def run(self):
        print("🤖 Rubico v1.2.0 running...")
        for update in self.updater.fetch():
            self.dispatcher.dispatch(update)
