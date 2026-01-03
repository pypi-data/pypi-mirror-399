class Message:
    def __init__(self, update, client):
        self.client = client
        self.update = update

        msg = update.get("message", {})
        self.text = msg.get("text", "")
        self.chat_id = msg.get("chat", {}).get("id")
        self.sender_id = msg.get("from", {}).get("id")

    def reply(self, text, keyboard=None):
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }
        if keyboard:
            payload["reply_markup"] = keyboard
        return self.client.call("sendMessage", payload)
