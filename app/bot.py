import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_config
from app.handlers.start import router as start_router

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    bot = Bot(token=config.bot.token, parse_mode="HTML")

    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())