from pydantic import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    SECRET_KEY: str
    DOMAIN_NAME: str
    ACME_EMAIL: str

    class Config:
        env_file = ".env.prod"

settings = Settings()