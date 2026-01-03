class CLIError(Exception):
    """Base class for all CLI tool errors."""

    pass


class APIError(CLIError):
    """Base class for all API errors."""

    pass


class ValidationError(CLIError):
    """An error that occurs when the user input is invalid."""

    pass


class ConversionError(CLIError):
    """An error that occurs when the converter function cannot convert the input."""

    pass
