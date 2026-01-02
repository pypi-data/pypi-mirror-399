from enum import Enum
from typing import Optional
from pydantic import BaseModel

class EmailStatus(str, Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class EmailResult(BaseModel):
    status: EmailStatus
    message_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    correlation_id: Optional[str] = None
