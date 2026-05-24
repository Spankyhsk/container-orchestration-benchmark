class ConnectionState:
    def __init__(self):
        self._items = {}

    def register(self, name, obj):
        self._items[name] = obj

    def unregister(self, name):
        self._items.pop(name, None)

    def all(self):
        return self._items