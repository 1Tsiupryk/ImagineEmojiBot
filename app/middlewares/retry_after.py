import asyncio
import logging

from aiogram import Bot
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType,
)
from aiogram.exceptions import TelegramRetryAfter
from aiogram.methods import Response, TelegramMethod
from aiogram.methods.base import TelegramType


logger = logging.getLogger(__name__)


class RetryAfterMiddleware(BaseRequestMiddleware):
    def __init__(
        self,
        max_retries: int = 3,
        delay_buffer: float = 0.5,
    ) -> None:
        self.max_retries = max_retries
        self.delay_buffer = delay_buffer

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        retries = 0
        method_name = type(method).__name__

        while True:
            try:
                return await make_request(bot, method)

            except TelegramRetryAfter as error:
                if retries >= self.max_retries:
                    logger.error(
                        "telegram_retry_exhausted "
                        "method=%s retries=%d retry_after=%s",
                        method_name,
                        retries,
                        error.retry_after,
                        exc_info=True,
                    )
                    raise

                retries += 1
                delay = error.retry_after + self.delay_buffer

                logger.warning(
                    "telegram_rate_limited "
                    "method=%s retry=%d/%d delay=%.1f",
                    method_name,
                    retries,
                    self.max_retries,
                    delay,
                )

                await asyncio.sleep(delay)