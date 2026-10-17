from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class Settings:
    PROJECT_NAME: str = "ResQFlow"
    API_V1_STR: str = "/api"
    RESQFLOW_SMS_DEVICE_TOKEN: str = os.getenv(
    "RESQFLOW_SMS_DEVICE_TOKEN", ""
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "resqflow-super-secret-key-emergency-2026-disaster-relief"
    )

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Always use backend/resqflow.db locally,
    # regardless of the directory from which the app is started.
    BASE_DIR = Path(__file__).resolve().parent.parent
    DEFAULT_DATABASE_PATH = BASE_DIR / "resqflow.db"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
    )

    CORS_ORIGINS: list = ["*"]


settings = Settings()