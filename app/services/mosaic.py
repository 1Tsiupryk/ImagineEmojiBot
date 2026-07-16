from dataclasses import dataclass


TILE_SIZE = 100
MAX_TILES = 100


class MosaicSizeValidationError(ValueError):
    pass


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