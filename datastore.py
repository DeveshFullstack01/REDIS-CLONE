import time


class DataStore:
    """
    In-memory database with key expiration support.

    _data    : key -> value
    _expires : key -> unix timestamp when the key should die
    """

    def __init__(self):
        self._data = {}
        self._expires = {}

    def _is_expired(self, key):
        """True if the key has an expiry time that has already passed."""
        if key not in self._expires:
            return False
        return time.time() > self._expires[key]

    def _remove(self, key):
        """Delete a key from both dictionaries."""
        self._data.pop(key, None)
        self._expires.pop(key, None)

    def _check_expiry(self, key):
        """Lazy expiration: if the key is expired, remove it now."""
        if self._is_expired(key):
            self._remove(key)

    def set(self, key, value):
        self._data[key] = value
        # A fresh SET clears any old expiry -- the key becomes permanent.
        self._expires.pop(key, None)

    def get(self, key):
        self._check_expiry(key)
        return self._data.get(key)

    def delete(self, key):
        self._check_expiry(key)
        if key in self._data:
            self._remove(key)
            return True
        return False

    def exists(self, key):
        self._check_expiry(key)
        return key in self._data

    def set_expiry(self, key, seconds):
        """Mark a key to expire N seconds from now. Returns False if no such key."""
        self._check_expiry(key)
        if key not in self._data:
            return False
        self._expires[key] = time.time() + seconds
        return True

    def ttl(self, key):
        """
        Seconds left before the key expires.
        Returns -2 if the key doesn't exist, -1 if it exists but has no expiry.
        (These special values match real Redis.)
        """
        self._check_expiry(key)
        if key not in self._data:
            return -2
        if key not in self._expires:
            return -1
        return int(self._expires[key] - time.time())

    def persist(self, key):
        """Remove a key's expiry, making it permanent. Returns True if it had one."""
        self._check_expiry(key)
        if key in self._expires:
            del self._expires[key]
            return True
        return False