import asyncio
import datetime

class Scheduler:
    def __init__(self, adapter):
        self.adapter = adapter
        self.tasks = {}

    def every(self, interval, chat_id, message):
        async def task():
            while True:
                await self.adapter.send_message(chat_id, message)
                await asyncio.sleep(self._parse_interval(interval))
        t = asyncio.create_task(task())
        self.tasks[chat_id + message] = t
        return t

    def at(self, datetime_str, chat_id, message):
        async def task():
            dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            now = datetime.datetime.now()
            delay = (dt - now).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
            await self.adapter.send_message(chat_id, message)
        t = asyncio.create_task(task())
        self.tasks[chat_id + message] = t
        return t

    def cancel(self, task_id):
        t = self.tasks.get(task_id)
        if t:
            t.cancel()
            del self.tasks[task_id]

    def _parse_interval(self, interval):
        if interval.endswith("s"):
            return int(interval[:-1])
        elif interval.endswith("m"):
            return int(interval[:-1]) * 60
        elif interval.endswith("h"):
            return int(interval[:-1]) * 3600
        else:
            return int(interval)
