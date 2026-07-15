from io import BytesIO

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.services.image import (
    MAX_IMAGE_BYTES,
    ImageValidationError,
    validate_image
)
from app.states import EmojiCreation


router = Router()


@router.message(EmojiCreation.waiting_for_image)
async def handle_image(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.photo:
        attachment = message.photo[-1]

    elif (
        message.document
        and message.document.mime_type
        and message.document.mime_type.startswith("image/")
    ):
        attachment = message.document

    else:
        await message.answer(
            "Пожалуйста, отправь изображение как фото или файл."
        )
        return

    if (
        attachment.file_size is not None
        and attachment.file_size > MAX_IMAGE_BYTES
    ):
        await message.answer("Размер изображения не должен превышать 10 МБ.")
        return

    buffer = BytesIO()

    try:
        await bot.download(attachment, destination=buffer)

        image_info = validate_image(buffer.getvalue())

    except ImageValidationError as error:
        await message.answer(str(error))
        return

    await state.update_data(
        image_file_id=attachment.file_id,
        image_width=image_info.width,
        image_height=image_info.height,
        image_format=image_info.image_format,
    )

    await state.set_state(EmojiCreation.waiting_for_grid)

    await message.answer(
        f"Изображение принято: "
        f"{image_info.width} × {image_info.height} px.\n\n"
        "Теперь введи количество столбцов и строк.\n"
        "Например: 6 4"
    )