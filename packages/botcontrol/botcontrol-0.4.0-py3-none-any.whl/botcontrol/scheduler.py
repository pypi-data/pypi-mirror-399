from typing import Callable
import asyncio

class Scheduler:
    def __init__(self, adapter=None):
        self.adapter = adapter
        self.tasks: list = []

    def schedule(self, coro: Callable, delay: int):
        """اجرای تابع پس از مدت زمان مشخص"""
        async def wrapper():
            await asyncio.sleep(delay)
            await coro()
        self.tasks.append(wrapper)
