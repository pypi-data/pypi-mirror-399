class Keyboard:
    def __init__(self):
        self.buttons = []

    def add(self, text, row=False):
        if row:
            self.buttons.append([{"text": text}])
        else:
            if self.buttons and isinstance(self.buttons[-1], list):
                self.buttons[-1].append({"text": text})
            else:
                self.buttons.append([{"text": text}])
        return self

    def build(self):
        return {"keyboard": self.buttons, "resize_keyboard": True, "one_time_keyboard": True}
