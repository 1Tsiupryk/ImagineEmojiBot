import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_config
from app.handlers.start import router as start_router
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers.image import router as image_router
from app.handlers.cancel import router as cancel_router
from app.middlewares.access import AccessMiddleware

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    bot = Bot(token=config.bot_token)

    dispatcher = Dispatcher(storage=MemoryStorage())

    access_middleware = AccessMiddleware(allowed_user_ids=config.allowed_user_ids)
    dispatcher.message.outer_middleware(access_middleware)
    dispatcher.callback_query.outer_middleware(access_middleware)

    dispatcher.include_router(cancel_router)
    dispatcher.include_router(start_router)
    dispatcher.include_router(image_router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())