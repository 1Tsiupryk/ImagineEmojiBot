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

from app.services.mosaic import (
    MosaicSizeValidationError,
    parse_mosaic_size,
)


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

    await state.set_state(EmojiCreation.waiting_for_size)
    
    await message.answer(
    f"Изображение принято: "
    f"{image_info.width} × {image_info.height} px.\n\n"
    "Введи ширину и высоту итогового изображения.\n"
    "Оба значения должны быть кратны 100 и не должны "
    "превышать размер исходного изображения.\n\n"
    "Например: 600 400"
)

@router.message(EmojiCreation.waiting_for_size)
async def handle_size(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(
            "Отправь ширину и высоту текстом.\n"
            "Например: 600 400"
        )
        return

    data = await state.get_data()

    required_fields = {
        "image_file_id",
        "image_width",
        "image_height",
    }

    if not required_fields.issubset(data):
        await state.clear()
        await message.answer(
            "Данные изображения потеряны. Отправь /start, "
            "чтобы начать заново."
        )
        return

    try:
        mosaic_size = parse_mosaic_size(
            text=message.text,
            source_width=data["image_width"],
            source_height=data["image_height"],
        )
    except MosaicSizeValidationError as error:
        await message.answer(
            f"{error}\n\n"
            "Попробуй ещё раз. Например: 600 400"
        )
        return

    await state.update_data(
        target_width=mosaic_size.width,
        target_height=mosaic_size.height,
    )

    await state.set_state(EmojiCreation.processing)

    remove_background = data.get(
        "remove_background",
        False
    )

    background_text = (
        "будет удалён" if remove_background
        else "останется без изменений"
    )

    await message.answer(
        "Размер принят.\n\n"
        f"Итоговое изображение: "
        f"{mosaic_size.width} × {mosaic_size.height} px\n"
        f"Сетка: "
        f"{mosaic_size.columns} × {mosaic_size.rows}\n"
        f"Количество эмодзи: {mosaic_size.tile_count}\n"
        f"Размер одного эмодзи: 100 × 100 px\n"
        f"Фон: {background_text}\n\n"
        "Параметры сохранены. Далее добавим обработку."
    )