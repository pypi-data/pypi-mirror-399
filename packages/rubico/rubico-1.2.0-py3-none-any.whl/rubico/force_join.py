class ForceJoin:
    def __init__(self, channel_id):
        self.channel_id = channel_id

    def check(self, client, user_id):
        res = client.call("getChatMember", {
            "chat_id": self.channel_id,
            "user_id": user_id
        })
        return res.get("status") in ("member", "administrator", "creator")
