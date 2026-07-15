from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError


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