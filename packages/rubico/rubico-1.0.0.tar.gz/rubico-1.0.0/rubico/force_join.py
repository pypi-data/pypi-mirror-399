from .middlewares import Middleware

class ForceJoin(Middleware):
    def __init__(self, bot, channel_username, message=None):
        self.bot = bot
        self.channel = channel_username
        self.message = message or "❌ لطفا عضو کانال شوید"

    def before(self, ctx):
        joined = False  # TODO: replace with real API check
        if not joined:
            ctx.reply(self.message)
            return False
        return True
