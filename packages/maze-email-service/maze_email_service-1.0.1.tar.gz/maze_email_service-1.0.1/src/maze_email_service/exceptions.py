class EmailServiceException(Exception):
    pass

class EmailSendFailed(EmailServiceException):
    pass

class EmailTemplateError(EmailServiceException):
    pass

class AttachmentTooLarge(Exception):
    pass