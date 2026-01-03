import json, os, threading

class _PersistentState:
    _instances = {}

    def __new__(cls, path):
        path = os.path.abspath(path)

        if path in cls._instances:
            return cls._instances[path]

        instance = super().__new__(cls)
        cls._instances[path] = instance
        return instance

    def __init__(self, path):
        # Prevent re-initialization when __new__ returns an existing instance
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self._path = os.path.abspath(path)
        self._lock = threading.Lock()
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        os.replace(tmp, self._path)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        with self._lock:
            self._data[name] = value
            self._save()


class _Namespace:
    def __init__(self, root, key):
        self._root = root
        self._key = key

    def __getattr__(self, name):
        try:
            return self._root._data[self._key][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        with self._root._lock:
            bucket = self._root._data.setdefault(self._key, {})
            bucket[name] = value
            self._root._save()


class PersistentObject(_PersistentState):
    def namespace(self, name) -> _Namespace:
        return _Namespace(self, name)




__all__ = ["PersistentObject"]
