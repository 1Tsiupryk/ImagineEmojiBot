from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import (
    CallbackQuery,
    Message,
    TelegramObject,
)


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_id: int) -> None:
        self.allowed_user_id = allowed_user_id

    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, dict[str, Any]],
            Awaitable[Any],
        ],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
            chat = event.chat

        elif isinstance(event, CallbackQuery):
            user = event.from_user
            chat = (
                event.message.chat
                if event.message is not None
                else None
            )

        else:
            return None

        if user is None or user.id != self.allowed_user_id:
            return None

        if chat is None or chat.type != ChatType.PRIVATE:
            return None

        return await handler(event, data)