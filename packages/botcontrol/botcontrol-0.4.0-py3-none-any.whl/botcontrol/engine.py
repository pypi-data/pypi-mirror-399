from typing import Callable, Any, List, Dict

class BotEngine:
    def __init__(self):
        self.commands: Dict[str, Callable[[Any], Any]] = {}
        self.plugins: List[Any] = []
        self.engine_initialized: bool = True

    def add_command(self, name: str, func: Callable[[Any], Any]) -> None:
        """ثبت دستور جدید"""
        self.commands[name] = func

    def execute(self, name: str, context: Any) -> Any:
        """اجرای دستور بر اساس پیام"""
        if name in self.commands:
            return self.commands[name](context)
        return f"دستور '{name}' یافت نشد."

    def load_plugin(self, plugin: Any) -> None:
        """بارگذاری پلاگین"""
        self.plugins.append(plugin)
        plugin.setup(self)
