import asyncio
from .scheduler import Scheduler
from .permissions import Permissions
from .spy import SpyEngine
from .storage import Storage

class BotControl:
    def __init__(self, adapter):
        self.adapter = adapter
        self.scheduler = Scheduler(adapter)
        self.permissions = Permissions(adapter)
        self.spy = SpyEngine(adapter)
        self.storage = Storage()
        self.commands = {}

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator

    async def handle(self, ctx, cmd, args):
        if cmd in self.commands:
            await self.commands[cmd](ctx, args)
            self.spy.log(f"{ctx.user_id} executed {cmd}")
        else:
            await ctx.send(f"⚠️ دستور ناشناخته: {cmd}")
