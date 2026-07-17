from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.states import EmojiCreation


router = Router()


@router.message(Command("cancel"))
async def handle_cancel(
    message: Message,
    state: FSMContext,
) -> None:
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Сейчас нет активной операции."
        )
        return

    if current_state == EmojiCreation.processing.state:
        await message.answer(
            "Изображение уже обрабатывается. "
            "Дождись завершения операции."
        )
        return

    await state.clear()

    await message.answer(
        "Операция отменена.\n"
        "Отправь /start, чтобы начать заново."
    )