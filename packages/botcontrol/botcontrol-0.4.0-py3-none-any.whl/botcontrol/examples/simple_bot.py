from botcontrol.engine import BotEngine
from botcontrol.context import Context

bot = BotEngine()

def hello(ctx: Context):
    print(f"سلام {ctx.user_id}!")

bot.add_command("سلام", hello)

ctx = Context(user_id=123, chat_id=1)
bot.execute("سلام", ctx)
