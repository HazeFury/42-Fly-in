class CustomError(Exception):
    """Base class for custom errors."""
    pass


class ParseError(Exception):
    """
    Exception raised for errors occurring during the file parsing phase.
    """
    def __init__(self, message: str, line_number: int) -> None:
        self.message = message
        self.line_number = line_number
        super().__init__(
            f"Parse error at line {self.line_number}: {self.message}"
            )
