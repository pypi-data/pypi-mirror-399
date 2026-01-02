class BotControl:
    def __init__(self, adapter):
        self.adapter = adapter
        self.commands = {}
        self.scheduler = None
        self.permissions = None
        self.spy = None

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator

    async def handle_message(self, ctx):
        if self.spy:
            self.spy.log({
                "type": "message",
                "chat_id": ctx.chat_id,
                "user_id": ctx.user_id,
                "text": ctx.text
            })

        if not ctx.text.startswith("/"):
            return

        parts = ctx.text[1:].split()
        cmd = parts[0]
        args = parts[1:]

        if cmd in self.commands:
            await self.commands[cmd](ctx, args)
class SpyEngine:
    def __init__(self, storage):
        self.storage = storage

    def log(self, data):
        self.storage.save(data)
