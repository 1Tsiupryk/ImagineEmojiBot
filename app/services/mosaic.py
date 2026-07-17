from dataclasses import dataclass

from aiogram.enums import MessageEntityType
from aiogram.types import MessageEntity

TILE_SIZE = 100
MAX_TILES = 100
FALLBACK_EMOJI = "🟦"

class MosaicSizeValidationError(ValueError):
    pass

class MosaicBuildError(ValueError):
    pass

@dataclass(frozen=True)
class CustomEmojiMosaic:
    text: str
    entities: tuple[MessageEntity, ...]

@dataclass(frozen=True)
class MosaicSize:
    width: int
    height: int

    @property
    def columns(self) -> int:
        return self.width // TILE_SIZE

    @property
    def rows(self) -> int:
        return self.height // TILE_SIZE

    @property
    def tile_count(self) -> int:
        return self.columns * self.rows


def parse_mosaic_size(text: str, source_width: int, source_height: int) -> MosaicSize:
    normalized = (
        text.lower()
        .replace("×", " ")
        .replace("x", " ")
        .replace("х", " ")
    )

    parts = normalized.split()

    if len(parts) != 2:
        raise MosaicSizeValidationError(
            "Введи ширину и высоту итогового изображения."
        )

    try:
        width, height = map(int, parts)
    except ValueError as error:
        raise MosaicSizeValidationError(
            "Ширина и высота должны быть целыми числами."
        ) from error

    if width < TILE_SIZE or height < TILE_SIZE:
        raise MosaicSizeValidationError(
            f"Минимальная ширина и высота: {TILE_SIZE} px."
        )

    if width % TILE_SIZE != 0 or height % TILE_SIZE != 0:
        raise MosaicSizeValidationError(
            f"Ширина и высота должны быть кратны {TILE_SIZE}."
        )

    if width > source_width or height > source_height:
        raise MosaicSizeValidationError(
            "Итоговый размер не должен превышать размер "
            f"исходного изображения: "
            f"{source_width} × {source_height} px."
        )

    mosaic_size = MosaicSize(
        width=width,
        height=height
    )

    if mosaic_size.tile_count > MAX_TILES:
        raise MosaicSizeValidationError(
            f"Максимальное количество эмодзи: {MAX_TILES}."
        )

    return mosaic_size


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def build_custom_emoji_mosaic(
    custom_emoji_ids: tuple[str, ...],
    columns: int,
    rows: int
) -> CustomEmojiMosaic:
    if columns < 1 or rows < 1:
        raise MosaicBuildError(
            "Размер сетки должен быть больше нуля."
        )

    expected_count = columns * rows

    if len(custom_emoji_ids) != expected_count:
        raise MosaicBuildError(
            "Количество custom emoji ID не соответствует размеру сетки."
        )

    text_parts: list[str] = []
    entities: list[MessageEntity] = []

    current_offset = 0
    fallback_length = utf16_length(FALLBACK_EMOJI)

    for index, custom_emoji_id in enumerate(custom_emoji_ids):
        if not custom_emoji_id:
            raise MosaicBuildError(
                "Получен пустой custom emoji ID."
            )

        text_parts.append(FALLBACK_EMOJI)

        entities.append(
            MessageEntity(
                type=MessageEntityType.CUSTOM_EMOJI,
                offset=current_offset,
                length=fallback_length,
                custom_emoji_id=custom_emoji_id,
            )
        )

        current_offset += fallback_length

        is_end_of_row = (index + 1) % columns == 0
        is_last_emoji = index + 1 == expected_count

        if is_end_of_row and not is_last_emoji:
            text_parts.append("\n")
            current_offset += utf16_length("\n")

    return CustomEmojiMosaic(
        text="".join(text_parts),
        entities=tuple(entities),
    )