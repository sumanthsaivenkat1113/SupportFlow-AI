from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str

    FRONTEND_URL: str

    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str | None = None
    HUGGINGFACE_API_TOKEN: str | None = None
    LLM_MODEL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",
    )


settings = Settings()
