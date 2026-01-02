import asyncio
from botcontrol import BotEngine, BotContext
from botcontrol.adapter.rubka_adapter import RubkaAdapter

engine = BotEngine()
adapter = RubkaAdapter()
engine.register_adapter(adapter)

async def hello(ctx: BotContext, args):
    await ctx.send(f"سلام {ctx.user_id}! شما دستور hello رو اجرا کردید.")

engine.add_command("hello", hello)

async def main():
    ctx = BotContext(user_id=123, message="hello", adapter=adapter)
    await engine.execute("hello", ctx, [])

asyncio.run(main())
