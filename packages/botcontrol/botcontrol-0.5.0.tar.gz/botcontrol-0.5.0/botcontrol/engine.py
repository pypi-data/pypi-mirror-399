from typing import Callable, Dict, Any, List
from .spy import SpyEngine
from .scheduler import Scheduler
from .permissions import Permissions
from .storage import Storage
from .context import BotContext

class BotEngine:
    def __init__(self):
        self.commands: Dict[str, Callable[[BotContext, List[str]], Any]] = {}
        self.adapters: List[Any] = []
        self.scheduler = Scheduler(self)
        self.permissions = Permissions()
        self.spy = SpyEngine()
        self.storage = Storage()

    def add_command(self, name: str, func: Callable[[BotContext, List[str]], Any]):
        """ثبت دستور جدید"""
        self.commands[name] = func

    async def execute(self, name: str, context: BotContext, args: list):
        """اجرای دستور بر اساس پیام"""
        if name in self.commands:
            await self.commands[name](context, args)
            self.spy.log(f"{context.user_id} executed {name}")
        else:
            await context.send(f"⚠️ دستور ناشناخته: {name}")

    def register_adapter(self, adapter):
        self.adapters.append(adapter)
        adapter.setup(self)
