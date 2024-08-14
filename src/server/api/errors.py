"""Api Error"""

from enum import IntEnum

class ApiErrorCode(IntEnum):
    DriverLoadFailure = 1
    InvalidOperation = 2
    TimeoutError = 10
    ConnectionError = 20
    UnknownObjectIDError = 30
    GeneralError = 100
    DriverNotFound = 101
    RuntimeError = 200
    DuplicateEntry = 201
    Unauthorized = 300

class ApiError(RuntimeError):
    def __init__(self, error_code: ApiErrorCode, message: str):
        self.error_code = error_code
        self.message = message
        # Needed for serialization support (Celery)
        # (https://docs.celeryq.dev/en/stable/userguide/tasks.html#creating-pickleable-exceptions)
        super().__init__(error_code, message)

    def to_json(self):
        return f"""{{ "errorCode": {self.error_code}, "message": {self.message} }}"""

class DriverLoadError(ApiError):
    def __init__(self, message: str):
        super().__init__(ApiErrorCode.DriverLoadFailure, message)

class DriverNotFoundError(ApiError):
    def __init__(self, message: str):
        super().__init__(ApiErrorCode.DriverNotFound, message)

class InvalidOperationError(ApiError):
    def __init__(self, message: str):
        super().__init__(ApiErrorCode.InvalidOperation, message)

class AuthError(ApiError):
    def __init__(self, message: str, error_code: ApiErrorCode = ApiErrorCode.Unauthorized):
        super().__init__(error_code, message)
