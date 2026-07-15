from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
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
async def handle_start(message: Message) -> None:
    await message.answer("Привет! Я помогу тебе создать набор эмодзи из твоего изображения!\n\n"
                         "Нужно ли удалить фон?", 
                         reply_markup=background_keyboard
                         )
    

@router.callback_query(F.data.startswith("background:"))
async def handle_background_choice(callback: CallbackQuery) -> None:
    await callback.answer()

    remove_background = callback.data == "background:remove"

    if callback.message is None:
        return
    
    if remove_background:
        response = "Хорошо, фон будет удалён."
    else:
        response = "Хорошо, фон останется без изменений."

    await callback.message.edit_text(
        f"{response}\n\nТеперь отправь изображение."
    )