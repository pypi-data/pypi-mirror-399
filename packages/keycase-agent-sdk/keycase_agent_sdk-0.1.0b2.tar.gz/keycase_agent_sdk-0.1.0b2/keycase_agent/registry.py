# registry.py
class KeywordRegistry:
    def __init__(self):
        self.keywords = {}

    def register(self, func):
        name = getattr(func, "keyword_name", None)
        if name:
            self.keywords[name] = func

    def get(self, name):
        return self.keywords.get(name)


keyword_registry = KeywordRegistry()
