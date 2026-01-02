from typing import List, Dict, Optional
from pydantic import BaseModel, EmailStr, Field
import base64
import mimetypes
import os

class EmailAttachment(BaseModel):
    filename: str
    content_base64: str
    content_type: str

    @staticmethod
    def from_file(file_path: str) -> "EmailAttachment":
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"

        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        return EmailAttachment(
            filename=os.path.basename(file_path),
            content_base64=encoded,
            content_type=mime_type
        )


class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    template_html: str
    variables: Dict[str, str]
    from_email: Optional[EmailStr] = None
    correlation_id: Optional[str] = None
    attachments: Optional[List[EmailAttachment]] = Field(default_factory=list)
