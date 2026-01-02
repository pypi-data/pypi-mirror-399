from .engine import BotControl
from .context import Context
class SpyEngine:
    def __init__(self, storage):
        self.storage = storage

    def log(self, data):
        self.storage.save(data)
