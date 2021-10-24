import secrets
from pydantic import AnyHttpUrl, BaseSettings
from typing import List, Union, Optional


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "ZC Messaging"


settings = Settings()
