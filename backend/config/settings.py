import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Class to hold application config values"""

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "ZC Messaging"


settings = Settings()
