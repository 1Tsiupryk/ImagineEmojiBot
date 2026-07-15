import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_config
from app.handlers.start import router as start_router
from aiogram.fsm.storage.memory import MemoryStorage

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    bot = Bot(token=config.bot_token)

    #temporary storage for FSM
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(start_router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())