from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_NAME: str = "Anon Chat"

    # 이메일 인증 코드
    EMAIL_CODE_EXPIRE_MINUTES: int = 10   # 코드 만료 (분)
    EMAIL_CODE_MAX_ATTEMPTS: int = 5      # 최대 시도 횟수

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()