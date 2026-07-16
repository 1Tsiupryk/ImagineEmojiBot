from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from rembg import remove as remove_background_image

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int
    image_format: str

TILE_SIZE = 100


class ImageProcessingError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProcessedMosaic:
    tiles: tuple[bytes, ...]
    columns: int
    rows: int

    @property
    def tile_count(self) -> int:
        return len(self.tiles)
    

def validate_image(image_bytes: bytes) -> ImageInfo:
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ImageValidationError("Размер изображения не должен превышать 10 МБ.")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            image_format = image.format or "UNKNOWN"

            if width * height > MAX_IMAGE_PIXELS:
                raise ImageValidationError("Изображение содержит слишком много пикселей.")

            if image_format not in ALLOWED_FORMATS:
                raise ImageValidationError("Поддерживаются только JPEG, PNG и WebP.")

            image.verify()

    except ImageValidationError:
        raise
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError,
    ) as error:
        raise ImageValidationError("Не удалось прочитать изображение.") from error

    return ImageInfo(
        width=width,
        height=height,
        image_format=image_format,
    )

def create_mosaic_tiles(
    image_bytes: bytes,
    target_width: int,
    target_height: int,
    should_remove_background: bool,
) -> ProcessedMosaic:
    if (
        target_width < TILE_SIZE
        or target_height < TILE_SIZE
        or target_width % TILE_SIZE != 0
        or target_height % TILE_SIZE != 0
    ):
        raise ImageProcessingError(
            "Некорректный размер итогового изображения."
        )

    processed_bytes = image_bytes

    if should_remove_background:
        try:
            processed_bytes = remove_background_image(image_bytes)
        except Exception as error:
            raise ImageProcessingError(
                "Не удалось удалить фон изображения."
            ) from error

    try:
        with Image.open(BytesIO(processed_bytes)) as source:
            resized = source.convert("RGBA").resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS,
            )

            columns = target_width // TILE_SIZE
            rows = target_height // TILE_SIZE
            tiles: list[bytes] = []

            try:
                for row in range(rows):
                    for column in range(columns):
                        left = column * TILE_SIZE
                        top = row * TILE_SIZE

                        tile = resized.crop(
                            (
                                left,
                                top,
                                left + TILE_SIZE,
                                top + TILE_SIZE
                            )
                        )

                        try:
                            buffer = BytesIO()
                            tile.save(buffer, format="PNG")
                            tiles.append(buffer.getvalue())
                        finally:
                            tile.close()
            finally:
                resized.close()

    except (UnidentifiedImageError, OSError) as error:
        raise ImageProcessingError(
            "Не удалось обработать изображение."
        ) from error

    if not tiles:
        raise ImageProcessingError(
            "После обработки не было создано ни одного тайла."
        )

    return ProcessedMosaic(
        tiles=tuple(tiles),
        columns=columns,
        rows=rows,
    )