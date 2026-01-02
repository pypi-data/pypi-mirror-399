from asyncio.log import logger
from azure.core.exceptions import AzureError
import time
from .config import settings
from .client import get_email_client
from .exceptions import AttachmentTooLarge
from .models import EmailRequest
from .result import EmailResult, EmailStatus
from .templates import render_template


def _validate_attachments(attachments):
    for attachment in attachments:
        size_mb = (len(attachment.content_base64) * 3) / (4 * 1024 * 1024)
        if size_mb > settings.MAX_ATTACHMENT_SIZE_MB:
            raise AttachmentTooLarge(
                f"{attachment.filename} exceeds {settings.MAX_ATTACHMENT_SIZE_MB}MB limit"
            )



def send_email(request: EmailRequest) -> EmailResult:
    correlation_id = request.correlation_id
    from_email = request.from_email or settings.FROM_EMAIL_ADDRESS

    try:
        html_content = render_template(
            request.template_html,
            request.variables
        )

        _validate_attachments(request.attachments)

    except AttachmentTooLarge as ex:
        return EmailResult(
            status=EmailStatus.FAILED,
            error_code="ATTACHMENT_TOO_LARGE",
            error_message=str(ex),
            correlation_id=correlation_id
            )
    except Exception as ex:
        logger.exception("Template rendering failed")
        return EmailResult(
            status=EmailStatus.FAILED,
            error_code="TEMPLATE_ERROR",
            error_message=str(ex),
            correlation_id=correlation_id
        )

    client = get_email_client()

    message = {
        "senderAddress": from_email,
        "recipients": {
            "to": [{"address": email} for email in request.to]
        },
        "content": {
            "subject": request.subject,
            "html": html_content
        }
    }
    if request.attachments:
        message["attachments"] = [
            {
                "name": att.filename,
                "contentType": att.content_type,
                "contentInBase64": att.content_base64
            }
            for att in request.attachments
        ]

    for attempt in range(1, settings.MAX_RETRIES + 1):
        try:
            poller = client.begin_send(message)
            result = poller.result()

            logger.info("Email sent successfully",
                        extra={"message_id": result["id"]})

            return EmailResult(
                status=EmailStatus.SENT,
                message_id=result["id"],
                correlation_id=correlation_id
            )

        except AzureError as ex:
            logger.warning(
                f"Email send attempt {attempt} failed: {ex}"
            )

            if attempt == settings.MAX_RETRIES:
                return EmailResult(
                    status=EmailStatus.FAILED,
                    error_code="ACS_SEND_FAILED",
                    error_message=str(ex),
                    correlation_id=correlation_id
                )

            time.sleep(settings.RETRY_BACKOFF_SECONDS * attempt)

    return EmailResult(
        status=EmailStatus.FAILED,
        error_code="UNKNOWN",
        error_message="Unknown email failure",
        correlation_id=correlation_id
    )


