from abc import ABC, abstractmethod
from ..context import Context

class BaseAdapter(ABC):
    @abstractmethod
    def send_message(self, context: Context, text: str):
        pass

    @abstractmethod
    def receive_message(self):
        pass
