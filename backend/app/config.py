from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    ai_model: str = "claude-sonnet-4-20250514"
    hf_token: str = ""
    hf_model: str = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
    api_key: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
