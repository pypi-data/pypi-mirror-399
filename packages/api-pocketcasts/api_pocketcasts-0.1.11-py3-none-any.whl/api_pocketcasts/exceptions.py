class PocketCastsAPIError(Exception):
    """
    Base exception for all Pocket Casts API errors.

    Args:
        code (str): A short error code identifying the error type.
        message (str): A human-readable error message.
        details (dict, optional): Additional error details (e.g., server response, context).
    """

    def __init__(self, code: str, message: str, details: dict = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"[{self.code}] {self.message} (" f"{self.details})"
        return f"[{self.code}] {self.message}"


class PocketCastsAPIResponseError(PocketCastsAPIError):
    """
    Raised for malformed or unexpected API responses (e.g., missing fields, invalid JSON).
    Inherits the standard error structure from PocketCastsAPIError.
    """

    def __init__(
        self,
        message: str = "Malformed or unexpected API response.",
        details: dict = None,
    ):
        super().__init__(
            code="api_response_error",
            message=message,
            details=details,
        )


class PocketCastsAuthError(PocketCastsAPIError):
    """
    Raised for authentication errors with the Pocket Casts API.
    Inherits the standard error structure from PocketCastsAPIError.
    """

    def __init__(self, message: str = "Authentication failed.", details: dict = None):
        super().__init__(code="auth_error", message=message, details=details)


class PocketCastsTokenExpiredError(PocketCastsAuthError):
    """
    Raised when the access token is expired or invalid.
    Inherits the standard error structure from PocketCastsAuthError.
    """

    def __init__(
        self, message: str = "Access token expired or invalid.", details: dict = None
    ):
        super().__init__(message=message, details=details)
