class BaseAdapter:
    def setup(self, engine):
        self.engine = engine

    async def send_message(self, user_id, text: str):
        raise NotImplementedError("send_message باید در Adapter پیاده‌سازی شود")
