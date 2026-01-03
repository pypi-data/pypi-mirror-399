class Context:
    def __init__(self, bot, message, storage):
        self.bot = bot
        self.message = message
        self.storage = storage

    def reply(self, text, keyboard=None):
        chat_id = self.message["chat"]["id"]
        self.bot.send_message(chat_id, text, keyboard)
