from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Model Config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Databricks
    DATABRICKS_HOST: str
    DATABRICKS_TOKEN: str
    DATABRICKS_INDEX_NAME: str

    # App
    USER_AGENT: str

# Instantiate settings
settings = Settings()
