import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Class to hold application config values."""

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "ZC Messaging"
    PLUGIN_KEY: str = "chat.zuri.chat"
    BASE_URL: str = "https://staging.api.zuri.chat"
    MESSAGE_COLLECTION = "messages"
    ROOM_COLLECTION = "rooms"


settings = Settings()
