from .middlewares import Middleware

class ForceJoin(Middleware):
    def __init__(self, bot, channel, text="❌ عضو کانال شو"):
        self.bot = bot
        self.channel = channel
        self.text = text

    def before(self, ctx):
        try:
            res = self.bot.client.call("getChatMember", {
                "chat_id": self.channel,
                "user_id": ctx.message.chat_id
            })
            status = res["result"]["status"]
            if status not in ("member", "administrator", "creator"):
                ctx.reply(self.text)
                return False
            return True
        except:
            ctx.reply(self.text)
            return False
