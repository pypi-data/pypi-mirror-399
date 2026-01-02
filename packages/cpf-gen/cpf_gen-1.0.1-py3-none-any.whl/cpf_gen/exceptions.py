class CpfGeneratorError(Exception):
    """Base exception for all cpf-gen related errors."""


class CpfGeneratorPrefixLengthError(CpfGeneratorError):
    """Raised when the prefix length is too long."""

    def __init__(self, prefix_length: int, max_length: int) -> None:
        self.prefix_length = prefix_length
        self.max_length = max_length

        super().__init__(
            f"The prefix length must be less than or equal to {max_length}. Got {prefix_length}."
        )


class CpfGeneratorPrefixNotValidError(CpfGeneratorError):
    """Raised when the prefix is not valid (e.g., repeated digits)."""

    def __init__(self, actual_prefix: str | list[str] | list[int], reason: str) -> None:
        self.actual_prefix = actual_prefix
        self.reason = reason

        super().__init__(f'The prefix "{actual_prefix}" is invalid. {reason}')
