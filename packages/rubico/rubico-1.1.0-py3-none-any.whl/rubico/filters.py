class TextFilter:
    def __init__(self, text):
        self.text = text

    def check(self, msg):
        return msg.get("text") == self.text

class ContainsFilter:
    def __init__(self, word):
        self.word = word

    def check(self, msg):
        return self.word in msg.get("text", "")

class AnyFilter:
    def __init__(self, *filters):
        self.filters = filters

    def check(self, msg):
        if not self.filters:
            return True
        return any(f.check(msg) for f in self.filters)
