class Keyboard:
    @staticmethod
    def simple(buttons):
        return {
            "keyboard": [[{"text": b} for b in buttons]],
            "resize_keyboard": True
        }
