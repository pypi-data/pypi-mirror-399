import time
from .client import RubicoClient
from .updater import UpdateManager
from .dispatcher import Dispatcher
from .handlers import Handler
from .filters import AnyFilter
from .commands import Command
from .context import Context
from .storage import Storage
from .steps import StepHandler
from .logger import Logger

class Bot:
    def __init__(self, token):
        self.client = RubicoClient(token)
        self.updater = UpdateManager(self.client)
        self.dispatcher = Dispatcher()
        self.commands = []
        self.middlewares = []
        self.storage = Storage()
        self.steps = StepHandler()
        self.logger = Logger()

    def use(self, mw):
        self.middlewares.append(mw)

    def command(self, name):
        def deco(fn):
            self.commands.append(Command(name, fn))
            return fn
        return deco

    def on_message(self):
        def deco(fn):
            self.dispatcher.add_handler(Handler(fn, AnyFilter()))
            return fn
        return deco

    def send_message(self, chat_id, text, keyboard=None):
        data = {"chat_id": chat_id, "text": text}
        if keyboard:
            data["reply_markup"] = keyboard.build()
        self.client.call("sendMessage", data)

    def run(self):
        print("🤖 Rubico v1.1.0 running...")
        while True:
            for msg in self.updater.fetch():
                ctx = Context(self, msg, self.storage)

                for mw in self.middlewares:
                    if not mw.before(ctx):
                        break
                else:
                    for cmd in self.commands:
                        if cmd.check(msg):
                            cmd.callback(ctx)
                            break
                    else:
                        self.dispatcher.dispatch(msg)
            time.sleep(1)
