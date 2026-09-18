import os

APP_DIR = os.path.join(os.path.dirname(__file__), "backend", "app")

config_code = """import os

class Settings:
    PROJECT_NAME: str = "ResQFlow AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "resqflow-super-secret-key-emergency-2026-disaster-relief")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resqflow.db")
    CORS_ORIGINS: list = ["*"]

settings = Settings()
"""

db_code = """from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

with open(os.path.join(APP_DIR, "config.py"), "w", encoding="utf-8") as f:
    f.write(config_code)

with open(os.path.join(APP_DIR, "database.py"), "w", encoding="utf-8") as f:
    f.write(db_code)

print("config.py and database.py written successfully.")
