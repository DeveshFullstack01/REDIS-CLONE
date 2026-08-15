class DataStore:
    """
    The in-memory database. Holds all key-value pairs and provides
    a clean set of methods to work with them. Networking code never
    touches the underlying dictionary directly -- it goes through here.
    """

    def __init__(self):
        # The actual storage. Private by convention (leading underscore).
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        # Returns the value, or None if the key doesn't exist.
        return self._data.get(key)

    def delete(self, key):
        # Returns True if a key was deleted, False if it wasn't there.
        if key in self._data:
            del self._data[key]
            return True
        return False

    def exists(self, key):
        return key in self._data