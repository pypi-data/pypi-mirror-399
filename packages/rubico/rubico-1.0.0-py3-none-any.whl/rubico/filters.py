class TextFilter:
    def __init__(self, text):
        self.text = text

    def check(self, message):
        return message.get("text") == self.text

class ContainsFilter:
    def __init__(self, keyword):
        self.keyword = keyword

    def check(self, message):
        return self.keyword in message.get("text", "")

class AnyFilter:
    def __init__(self, *filters):
        self.filters = filters

    def check(self, message):
        if not self.filters:
            return True
        return any(f.check(message) for f in self.filters)
