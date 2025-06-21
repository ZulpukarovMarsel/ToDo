from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    # Project data
    PROJECT_NAME: str = "ToDo"
    PROJECT_DESCRIPTION: str = "Hello worlds!\nIt's project ToDo"

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Smtp Email
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Database url
    @property
    def DATA_BASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # env file settings
    model_config = SettingsConfigDict(env_file=".env")


settings = Setting()
