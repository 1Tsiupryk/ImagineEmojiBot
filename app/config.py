import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    allowed_user_id: int


def load_config() -> Config:
    load_dotenv()

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not configured."
        )

    raw_user_id = os.getenv("ALLOWED_USER_ID")
    if not raw_user_id:
        raise RuntimeError(
            "ALLOWED_USER_ID environment variable is not configured."
        )

    try:
        allowed_user_id = int(raw_user_id)
    except ValueError as error:
        raise RuntimeError(
            "ALLOWED_USER_ID must be an integer."
        ) from error

    return Config(
        bot_token=token,
        allowed_user_id=allowed_user_id,
    )