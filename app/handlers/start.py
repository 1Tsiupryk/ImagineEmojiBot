from email import message

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.fsm.context import FSMContext
from app.states import EmojiCreation
from aiogram.filters import CommandStart

router = Router()

background_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Удалить фон",
                callback_data="background:remove"
            ),
            InlineKeyboardButton(
                text="Оставить фон",
                callback_data="background:keep"
            )
        ]
    ]
)

@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == EmojiCreation.processing.state:
        await message.answer(
            "Предыдущая операция ещё выполняется. "
            "Дождись её завершения."
        )
        return

    await state.clear()
    await state.set_state(EmojiCreation.choosing_background)

    await message.answer("Привет! Я помогу тебе создать набор эмодзи из твоего изображения!\n\n"
                         "Нужно ли удалить фон?", 
                         reply_markup=background_keyboard
                         )
    

@router.callback_query(EmojiCreation.choosing_background, F.data.startswith("background:"))
async def handle_background_choice(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    remove_background = callback.data == "background:remove"

    await state.update_data(remove_background=remove_background)
    await state.set_state(EmojiCreation.waiting_for_image)

    if callback.message is None:
        return
    
    if remove_background:
        response = "Хорошо, фон будет удалён."
    else:
        response = "Хорошо, фон останется без изменений."

    await callback.message.edit_text(
        f"{response}\n\nТеперь отправь изображение."
    )