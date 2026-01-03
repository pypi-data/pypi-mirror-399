import typing


class InvalidArgumentsError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoConfigSetError(Exception):
    def __init__(self, message: typing.Optional[str] = None):
        message = (
            message
            if message
            else "Config must be set for this to work. Use `heisenberg-cli configure` to set necessary settings"
        )
        super().__init__(message)


class InvalidJobIgnore(Exception):
    def __init__(self, message=None):
        message = message or ".jobignore file is invalid"
        super().__init__(message)


class EncryptionError(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class EnvFileNotFound(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class RestClientException(Exception):
    """Base exception for REST client errors"""

    def __init__(self, message):
        super().__init__(message)


class BadRequestError(RestClientException):
    """400 Bad Request"""

    pass


class UnauthorizedError(RestClientException):
    """401 Unauthorized"""

    pass


class ForbiddenError(RestClientException):
    """403 Forbidden"""

    pass


class NotFoundError(RestClientException):
    """404 Not Found"""

    pass


class ServerError(RestClientException):
    """5xx Server Error"""

    pass
