from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application configuration settings"""

    # Gmail API
    gmail_credentials_path: str = Field(default="credentials.json")
    gmail_token_path: str = Field(default="token.json")

    # AI Provider
    ai_provider: Literal["anthropic", "openai"] = Field(default="openai")
    anthropic_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")

    # Google Sheets
    google_sheets_id: str = Field(default="")

    # Application Settings
    email_check_interval: int = Field(default=300)
    max_emails_per_run: int = Field(default=50)
    reply_approval_required: bool = Field(default=True)

    # Classification
    priority_high_threshold: float = Field(default=0.7)
    priority_medium_threshold: float = Field(default=0.4)

    # Vector Store
    vector_store_path: str = Field(default="./data/vector_store")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")

    # Follow-up
    follow_up_days: int = Field(default=3)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
