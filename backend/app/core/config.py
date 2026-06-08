from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GITHUB_TOKEN: str | None = None
    OPENAI_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    GITHUB_API_URL: str = "https://api.github.com"
    OPENAI_API_URL: str = "https://api.openai.com/v1"
    DEEPSEEK_API_URL: str = "https://api.deepseek.com"

    timeout: int = 30


settings = Settings()