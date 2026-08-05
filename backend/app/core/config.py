import os

class Settings:
    PROJECT_NAME: str = "Arrow Escape"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-development-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

settings = Settings()
