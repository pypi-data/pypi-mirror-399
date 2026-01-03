import json
import os

class JsonStorage:
    def __init__(self, file="data.json"):
        self.file = file
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)

    def read(self):
        with open(self.file) as f:
            return json.load(f)

    def write(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)
