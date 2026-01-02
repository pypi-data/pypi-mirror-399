class Alerts:
    @staticmethod
    async def send_alert(context, message: str):
        await context.send(f"⚠️ ALERT: {message}")
