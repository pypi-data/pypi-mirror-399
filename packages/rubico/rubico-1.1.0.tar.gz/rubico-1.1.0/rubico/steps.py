class StepHandler:
    def __init__(self):
        self.steps = {}

    def set(self, user_id, step):
        self.steps[user_id] = step

    def get(self, user_id):
        return self.steps.get(user_id)

    def clear(self, user_id):
        self.steps.pop(user_id, None)
