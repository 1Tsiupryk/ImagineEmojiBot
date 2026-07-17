import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    allowed_user_ids: frozenset[int]


def load_config() -> Config:
    load_dotenv()

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not configured."
        )

    raw_user_ids = os.getenv("ALLOWED_USER_IDS")
    if not raw_user_ids:
        raise RuntimeError(
            "ALLOWED_USER_IDS environment variable is not configured."
        )

    try:
        allowed_user_ids = frozenset(
            int(item.strip())
            for item in raw_user_ids.split(",")
            if item.strip()
        )
    except ValueError as error:
        raise RuntimeError(
            "ALLOWED_USER_IDS must contain comma-separated integers."
        ) from error

    if not allowed_user_ids:
        raise RuntimeError(
            "ALLOWED_USER_IDS must contain at least one user ID."
        )

    return Config(
        bot_token=token,
        allowed_user_ids=allowed_user_ids,
    )