from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    app_base_url: str = Field(default="https://app.orvya.net", alias="APP_BASE_URL")
    admin_base_url: str = Field(default="https://admin.orvya.net", alias="ADMIN_BASE_URL")
    session_secret: str | None = Field(default=None, alias="SESSION_SECRET")
    encryption_key: str | None = Field(default=None, alias="ENCRYPTION_KEY")
    smtp_host: str | None = Field(default=None, alias="SMTP_HOST")
    smtp_port: int | None = Field(default=None, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str | None = Field(default=None, alias="SMTP_FROM")
    s3_endpoint: str | None = Field(default=None, alias="S3_ENDPOINT")
    s3_region: str | None = Field(default=None, alias="S3_REGION")
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    cnj_base_url: str | None = Field(default=None, alias="CNJ_BASE_URL")
    cnj_token: str | None = Field(default=None, alias="CNJ_TOKEN")
    ops_token: str | None = Field(default=None, alias="OPS_TOKEN")


@lru_cache
def get_settings() -> Settings:
    return Settings()
