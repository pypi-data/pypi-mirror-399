import asyncio

class Scheduler:
    def __init__(self, engine):
        self.engine = engine

    async def schedule(self, delay: int, func, *args, **kwargs):
        await asyncio.sleep(delay)
        await func(*args, **kwargs)
