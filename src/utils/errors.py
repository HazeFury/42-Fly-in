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
             "\033[91m[LOCATION]\033[0m Error detected at line"
             f" : \033[93m{self.line_number}\033[0m:\n"
             f"\033[91m[CAUSE]\033[0m {self.message}\n\n"
             "\033[94m==== EXITING PROGRAM ====\033[0m"
            )
