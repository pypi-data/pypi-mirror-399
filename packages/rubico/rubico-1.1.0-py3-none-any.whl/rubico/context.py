class Message:
    def __init__(self, raw):
        self.raw = raw
        self.chat_id = raw["chat"]["id"]
        self.text = raw.get("text", "")
        self.user = raw.get("from", {})

class Context:
    def __init__(self, bot, raw_message, storage):
        self.bot = bot
        self.message = Message(raw_message)
        self.storage = storage

    def reply(self, text, keyboard=None):
        self.bot.send_message(self.message.chat_id, text, keyboard)
