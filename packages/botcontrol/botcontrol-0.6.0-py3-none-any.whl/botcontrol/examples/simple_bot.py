import asyncio
from botcontrol import BotEngine, Context

# نمونه BotEngine
bot = BotEngine()

# دستور ساده
def hello_command(ctx: Context):
    ctx.send(f"سلام کاربر {ctx.user_id}! پیام شما: {ctx.message}")

bot.add_command("سلام", hello_command)

# شبیه‌سازی پیام لوکال
messages = [
    Context(user_id=1, message="سلام"),
    Context(user_id=2, message="سلام")
]

for msg in messages:
    bot.execute("سلام", msg)
