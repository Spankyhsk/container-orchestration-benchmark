from collections import deque

class UILogger:

    def __init__(self, max_lines=200):
        self.logs = deque(maxlen=max_lines)

    def push(self, msg: str):
        print(msg)
        self.logs.appendleft(msg)

    def all(self):
        return list(self.logs)