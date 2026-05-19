import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    base_url: str
    model_name: str
    max_history_messages: int = 6


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    base_url = os.getenv("BASE_URL", "http://localhost:1234/v1")
    model_name = os.getenv("MODEL_NAME", "qwen/qwen2.5-7b-instruct")

    if not bot_token:
        raise ValueError("BOT_TOKEN is missing in .env file")

    return Config(
        bot_token=bot_token,
        base_url=base_url,
        model_name=model_name,
    )