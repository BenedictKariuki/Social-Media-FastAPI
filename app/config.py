from pydantic_settings import BaseSettings

# The BaseSettings class will look for environment variables that match the attributes' names
class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_password: str
    database_username: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()