from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    environment: str = "production"

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
