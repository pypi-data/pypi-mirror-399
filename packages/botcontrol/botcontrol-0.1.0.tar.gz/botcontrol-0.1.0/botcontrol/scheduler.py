import asyncio

class Scheduler:
    def __init__(self, adapter):
        self.adapter = adapter
        self.tasks = []

    def every(self, seconds, chat_id, text):
        async def job():
            while True:
                await asyncio.sleep(seconds)
                await self.adapter.send_message(chat_id, text)

        task = asyncio.create_task(job())
        self.tasks.append(task)
