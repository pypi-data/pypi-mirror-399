import os
from dotenv import load_dotenv
from typing import ClassVar
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):    
    AZURE_COMMUNICATION_CONNECTION_STRING : str = os.environ['AZURE_COMMUNICATION_CONNECTION_STRING']
    FROM_EMAIL_ADDRESS : str = os.environ['FROM_EMAIL_ADDRESS']
    MAX_RETRIES: ClassVar[int]  = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF_SECONDS: ClassVar[int] =int(os.getenv("RETRY_BACKOFF_SECONDS", "10"))
    MAX_ATTACHMENT_SIZE_MB: ClassVar[int] = int(os.getenv("MAX_ATTACHMENT_SIZE_MB", "10"))

settings = Settings()
