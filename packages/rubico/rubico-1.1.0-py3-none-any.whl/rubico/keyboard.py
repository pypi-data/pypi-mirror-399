class Keyboard:
    def __init__(self):
        self.rows = []

    def add(self, text, row=False):
        if row or not self.rows:
            self.rows.append([{"text": text}])
        else:
            self.rows[-1].append({"text": text})
        return self

    def build(self):
        return {
            "keyboard": self.rows,
            "resize_keyboard": True
        }
