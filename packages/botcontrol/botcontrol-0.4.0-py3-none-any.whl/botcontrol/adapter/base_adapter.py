from typing import Any

class BaseAdapter:
    async def send_message(self, chat_id: int, text: str) -> None:
        raise NotImplementedError

    async def get_updates(self) -> Any:
        raise NotImplementedError

    async def handle_message(self, message: Any) -> None:
        raise NotImplementedError
