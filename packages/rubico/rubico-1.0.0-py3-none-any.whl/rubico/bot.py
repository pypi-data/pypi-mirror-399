import time
from .client import RubicoClient
from .updater import UpdateManager
from .dispatcher import Dispatcher
from .handlers import Handler
from .filters import TextFilter, ContainsFilter, AnyFilter
from .keyboard import Keyboard
from .commands import Command
from .context import Context
from .storage import Storage
from .logger import Logger

class Bot:
    def __init__(self, token, db_path="rubico.db"):
        self.client = RubicoClient(token)
        self.updater = UpdateManager(self.client)
        self.dispatcher = Dispatcher()
        self.commands = []
        self.storage = Storage(db_path)  # SQLite حرفه‌ای
        self.middlewares = []
        self.logger = Logger()

    # --- Middleware ---
    def use(self, middleware):
        self.middlewares.append(middleware)

    def _run_middlewares_before(self, ctx):
        for m in self.middlewares:
            if hasattr(m, "before") and not m.before(ctx):
                self.logger.info(f"Middleware blocked: {m.__class__.__name__}")
                return False
        return True

    def _run_middlewares_after(self, ctx):
        for m in self.middlewares:
            if hasattr(m, "after"):
                m.after(ctx)

    # --- Commands ---
    def command(self, name):
        def decorator(func):
            self.commands.append(Command(name, func))
            return func
        return decorator

    def _handle_commands(self, message):
        for cmd in self.commands:
            if cmd.check(message):
                ctx = Context(self, message, self.storage)
                if not self._run_middlewares_before(ctx):
                    return True
                try:
                    cmd.callback(ctx)
                    self._run_middlewares_after(ctx)
                except Exception as e:
                    self.logger.error(f"Command error: {e}")
                return True
        return False

    # --- Message Handlers ---
    def on_message(self, text=None, contains=None):
        def decorator(func):
            filters = []
            if text:
                filters.append(TextFilter(text))
            if contains:
                filters.append(ContainsFilter(contains))
            filter_obj = AnyFilter(*filters) if filters else AnyFilter()
            self.dispatcher.add_handler(Handler(func, filter_obj))
            return func
        return decorator

    # --- Send Message ---
    def send_message(self, chat_id, text, keyboard=None):
        payload = {"chat_id": chat_id, "text": text}
        if keyboard:
            payload["reply_markup"] = keyboard.build()
        try:
            self.client.call("sendMessage", payload)
            self.logger.info(f"Sent message to {chat_id}")
        except Exception as e:
            self.logger.error(f"Send message error: {e}")

    # --- Dispatcher & Run ---
    def _dispatch(self, message):
        ctx = Context(self, message, self.storage)
        if not self._run_middlewares_before(ctx):
            return

        if self._handle_commands(message):
            return

        try:
            self.dispatcher.dispatch(message)
        except Exception as e:
            self.logger.error(f"Handler error: {e}")

        self._run_middlewares_after(ctx)

    def run(self, interval=1):
        print("🤖 rubico bot running (global pro mode)")
        while True:
            try:
                messages = self.updater.fetch()
                for msg in messages:
                    self._dispatch(msg)
            except Exception as e:
                self.logger.error(f"Updater loop error: {e}")
            time.sleep(interval)
