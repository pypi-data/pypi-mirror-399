import importlib


class Context(dict):
    def add_module(self, name, alias=None):
        if not alias:
            alias=name
        self[alias] = importlib.import_module(name)
