import secrets
from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    BufferedInputFile,
    InputSticker,
)

from app.services.mosaic import FALLBACK_EMOJI

INITIAL_STICKER_LIMIT = 50


class StickerSetCreationError(RuntimeError):
    def __init__(
        self,
        message: str,
        pack_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.pack_name = pack_name

    @property
    def pack_link(self) -> str | None:
        if self.pack_name is None:
            return None

        return f"https://t.me/addemoji/{self.pack_name}"


@dataclass(frozen=True)
class CustomEmojiPack:
    name: str
    link: str
    custom_emoji_ids: tuple[str, ...]


def generate_pack_name(
    user_id: int,
    bot_username: str,
) -> str:
    suffix = f"_by_{bot_username}"
    random_part = secrets.token_hex(4)

    prefix = f"mosaic_{user_id}_{random_part}"

    available_prefix_length = 64 - len(suffix)

    prefix = prefix[:available_prefix_length].rstrip("_")

    return f"{prefix}{suffix}"


def make_input_sticker(
    tile: bytes,
    position: int,
) -> InputSticker:
    return InputSticker(
        sticker=BufferedInputFile(
            tile,
            filename=f"tile_{position}.png",
        ),
        format="static",
        emoji_list=[FALLBACK_EMOJI],
    )


async def create_custom_emoji_pack(
    bot: Bot,
    user_id: int,
    tiles: tuple[bytes, ...],
) -> CustomEmojiPack:
    if not tiles:
        raise StickerSetCreationError(
            "Нельзя создать пустой набор эмодзи."
        )

    me = await bot.get_me()

    if not me.username:
        raise StickerSetCreationError(
            "У бота отсутствует username."
        )

    pack_name = generate_pack_name(
        user_id=user_id,
        bot_username=me.username,
    )

    pack_title = "Emoji pack by @gaxillic"

    stickers = [
        make_input_sticker(
            tile=tile,
            position=index,
        )
        for index, tile in enumerate(tiles, start=1)
    ]

    initial_stickers = stickers[:INITIAL_STICKER_LIMIT]
    remaining_stickers = stickers[INITIAL_STICKER_LIMIT:]

    try:
        await bot.create_new_sticker_set(
            user_id=user_id,
            name=pack_name,
            title=pack_title,
            stickers=initial_stickers,
            sticker_type="custom_emoji",
        )
    except TelegramAPIError as error:
        raise StickerSetCreationError(
            "Telegram не смог создать набор эмодзи."
        ) from error

    # createNewStickerSet accepts at most 50 initial stickers.
    # Add any remaining tiles individually.
    try:
        for sticker in remaining_stickers:
            await bot.add_sticker_to_set(
                user_id=user_id,
                name=pack_name,
                sticker=sticker,
            )
    except TelegramAPIError as error:
        raise StickerSetCreationError(
            "Набор был создан, но добавить все эмодзи не удалось.",
            pack_name=pack_name,
        ) from error

    try:
        sticker_set = await bot.get_sticker_set(
            name=pack_name,
        )
    except TelegramAPIError as error:
        raise StickerSetCreationError(
            "Набор был создан, но получить его данные не удалось.",
            pack_name=pack_name,
        ) from error

    custom_emoji_ids = tuple(
        sticker.custom_emoji_id
        for sticker in sticker_set.stickers
        if sticker.custom_emoji_id is not None
    )

    if len(custom_emoji_ids) != len(tiles):
        raise StickerSetCreationError(
            "Telegram вернул неправильное количество custom emoji ID.",
            pack_name=pack_name,
        )

    return CustomEmojiPack(
        name=pack_name,
        link=f"https://t.me/addemoji/{pack_name}",
        custom_emoji_ids=custom_emoji_ids,
    )