import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass(frozen=True)
class Config:
    bot_token: str

def load_config() -> Config:
    load_dotenv()  # Load environment variables from .env file

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not configured.")
    
    return Config(bot_token=token)
