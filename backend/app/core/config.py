from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str

    FRONTEND_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",
    )


settings = Settings()
