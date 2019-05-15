class Error(Exception):
    """Base class for other exceptions"""
    pass


class ValidationError(Error):
    """Raised when the validation is error"""
    pass


class PermissionDenied(Exception):
    """The user did not have permission to do that"""
    pass
