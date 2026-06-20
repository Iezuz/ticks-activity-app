from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

RADIUS_OF_SEARCHING_FOR_STATIONS = 50000  # радиус поиска станций с данными о погоде
LIMIT_OF_STATIONS = 10  # количество искомых станций в радиусе
TEMP_THRESHOLD = 5.0  # пороговое значение температуры для определения даты начала сезона

LONG_MODEL_DIR = Path("backend/ml/dumps/long_model")
SHORT_MODEL_DIR = Path("backend/ml/dumps/short_model")


class Settings(BaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()

print("DB URL =>", settings.get_db_url())
print("DB HOST =>", settings.DB_HOST)





