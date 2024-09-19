from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Class responsible for parsing environment variables.
    Default looks for .env.development at the root of the project.
    Can be overridden by instantiating the class with a different env_file through _env_file parameter.
    Environment variables take priority over the .env files.
    """

    model_config = SettingsConfigDict(env_file=".env.development")

    LINKEDIN_EMAIL: str
    LINKEDIN_PASSWORD: str
    OPENAI_API_KEY: str
    MONGODB_URI: str
