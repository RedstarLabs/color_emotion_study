from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development", min_length=1)
    app_host: str = Field(default="127.0.0.1", min_length=1)
    app_port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = Field(
        default="sqlite:///./coloremotionstudy.db",
        min_length=1,
    )
    admin_api_token: str | None = None

    @model_validator(mode="after")
    def validate_production_database_path(self) -> Settings:
        if self.app_env.lower() in {
            "production",
            "prod",
        }:
            if self.app_host not in {"127.0.0.1", "localhost"}:
                raise ValueError("Production APP_HOST must be local.")
            if not self.admin_api_token or len(self.admin_api_token) < 32:
                raise ValueError(
                    "Production ADMIN_API_TOKEN must contain at least 32 characters."
                )
            if self.database_url.lower().startswith("sqlite"):
                prefix = "sqlite:///"
                if not self.database_url.startswith(prefix):
                    raise ValueError(
                        "Production SQLite DATABASE_URL must use sqlite:/// "
                        "with an absolute path."
                    )
                database_path = self.database_url.removeprefix(prefix)
                if (
                    not Path(database_path.split("?", maxsplit=1)[0]).is_absolute()
                    or "?" in database_path
                    or "#" in database_path
                ):
                    raise ValueError(
                        "Production SQLite DATABASE_URL must use an absolute "
                        "path without URI parameters."
                    )
        return self

    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
