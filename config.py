from pydantic_settings import BaseSettings
class Settings (BaseSettings):
    APP_NAME : str = "TaskFlow"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL : str
    DEBUG : bool = False
    # JWT settings
    ALGORITHM: str ="HS256"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    class Config:
        env_file = ".env"

settings = Settings()
