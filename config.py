from functools import lru_cache
from typing import List

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestUser(BaseModel):
    email: str
    username: str
    password: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # окружение
    env: str = "dev"

    # базовый URL
    base_url: str

    # браузеры, перечисленные через запятую в .env
    browsers_raw: str = "chromium"

    headless: bool = True

    # файлы
    browser_state_file: str = "browser-state.json"

    # тестовый пользователь
    test_user_email: str
    test_user_username: str
    test_user_password: str

    @property
    def browsers(self) -> List[str]:
        return [b.strip() for b in self.browsers_raw.split(",") if b.strip()]

    @property
    def test_user(self) -> TestUser:
        return TestUser(
            email=self.test_user_email,
            username=self.test_user_username,
            password=self.test_user_password,
        )

    def get_base_url(self) -> str:
        return self.base_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
