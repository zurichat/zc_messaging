import secrets

from pydantic import BaseSettings
import cloudinary
import os

from dotenv import load_dotenv

load_dotenv()



# cloudinary.config(
#     cloud_name = 'deizhrjy7',
#     api_key = 225348553815486,
#     api_secret = 'R-7ratXg_ALTCUoEvds9xnbfqiA'
# )

cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('API_KEY'),
    api_secret = os.getenv('API_SECRET')
)


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
