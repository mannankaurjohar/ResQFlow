import os

class Settings:
    PROJECT_NAME: str = "ResQFlow AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "resqflow-super-secret-key-emergency-2026-disaster-relief")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resqflow.db")
    CORS_ORIGINS: list = ["*"]

settings = Settings()
