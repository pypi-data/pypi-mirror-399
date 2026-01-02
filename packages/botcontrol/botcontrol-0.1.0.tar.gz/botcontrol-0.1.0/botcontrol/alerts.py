class AlertManager:
    def __init__(self, adapter, owner_id):
        self.adapter = adapter
        self.owner_id = owner_id

    async def alert(self, text):
        await self.adapter.send_message(
            self.owner_id,
            f"🚨 ALERT:\n{text}"
        )
