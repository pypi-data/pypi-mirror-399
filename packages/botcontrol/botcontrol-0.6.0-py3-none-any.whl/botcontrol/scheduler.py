import asyncio
from typing import Callable

class Scheduler:
    def __init__(self):
        self.tasks: list[asyncio.Task] = []

    async def schedule(self, delay: float, func: Callable):
        await asyncio.sleep(delay)
        await func()

    def add_task(self, delay: float, func: Callable):
        task = asyncio.create_task(self.schedule(delay, func))
        self.tasks.append(task)
