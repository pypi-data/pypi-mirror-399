import asyncio

class Scheduler:
    def __init__(self):
        self.tasks = []

    def schedule(self, delay, func, *args, **kwargs):
        """زمان‌بندی اجرای تابع"""
        async def task():
            await asyncio.sleep(delay)
            func(*args, **kwargs)
        self.tasks.append(asyncio.create_task(task()))
