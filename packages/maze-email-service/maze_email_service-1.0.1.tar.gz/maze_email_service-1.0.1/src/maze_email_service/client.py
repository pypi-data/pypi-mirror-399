from azure.communication.email import EmailClient
from .config import settings
def get_email_client():
    return EmailClient.from_connection_string(
        settings.AZURE_COMMUNICATION_CONNECTION_STRING
    )
