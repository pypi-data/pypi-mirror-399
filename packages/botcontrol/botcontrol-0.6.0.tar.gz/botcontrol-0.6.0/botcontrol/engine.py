from typing import Callable, Dict, List
from .context import Context

class BotEngine:
    def __init__(self):
        self.commands: Dict[str, Callable[[Context], None]] = {}
        self.plugins: List[Callable] = []

    def add_command(self, name: str, func: Callable[[Context], None]):
        """ثبت دستور جدید"""
        self.commands[name] = func

    def execute(self, name: str, context: Context):
        """اجرای دستور بر اساس پیام"""
        if name in self.commands:
            return self.commands[name](context)
        return f"دستور '{name}' یافت نشد."

    def load_plugin(self, plugin):
        """بارگذاری پلاگین"""
        self.plugins.append(plugin)
        plugin.setup(self)
