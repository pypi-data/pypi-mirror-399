import re
from dataclasses import dataclass, replace

from .exceptions import CpfGeneratorPrefixLengthError, CpfGeneratorPrefixNotValidError

CPF_LENGTH = 11
PREFIX_MAX_LENGTH = CPF_LENGTH - 2


@dataclass(slots=True, frozen=False)
class CpfGeneratorOptions:
    """Class to manage and store the options for the CPF generator."""

    format: bool | None = None
    prefix: str | None = None

    def __post_init__(self) -> None:
        if self.format is None:
            object.__setattr__(self, "format", False)
        if self.prefix is None:
            object.__setattr__(self, "prefix", "")

    def merge(
        self,
        format: bool | None = None,
        prefix: str | None = None,
    ) -> "CpfGeneratorOptions":
        """Creates a new instance of CpfGeneratorOptions with the given options merged with the current options."""
        kwargs = {}

        if format is not None:
            kwargs["format"] = format
        if prefix is not None:
            kwargs["prefix"] = prefix

        return replace(self, **kwargs)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "prefix" and value is not None:
            prefix_value = re.sub(r"[^0-9]", "", str(value))
            prefix_length = len(prefix_value)

            if prefix_length > PREFIX_MAX_LENGTH:
                raise CpfGeneratorPrefixLengthError(prefix_length, PREFIX_MAX_LENGTH)

            if prefix_length == PREFIX_MAX_LENGTH:
                digits_set = set(prefix_value)

                if len(digits_set) == 1:
                    raise CpfGeneratorPrefixNotValidError(
                        value,
                        "Repeated digits are not considered valid.",
                    )

            value = prefix_value

        object.__setattr__(self, name, value)
