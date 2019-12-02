import logging

logger = logging.getLogger(__name__)


class AWSException(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.status = status

        logger.warning(message)


class ClientCredentialsException(AWSException):
    pass


class AWSPermissionDenied(AWSException):
    pass


class OperationError(AWSException):
    pass
