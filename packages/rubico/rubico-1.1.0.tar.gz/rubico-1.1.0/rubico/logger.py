import datetime

class Logger:
    def info(self, msg):
        print(f"[INFO {datetime.datetime.now()}] {msg}")

    def error(self, msg):
        print(f"[ERROR {datetime.datetime.now()}] {msg}")
