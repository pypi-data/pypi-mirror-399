import random

from cpf_dv import CpfCheckDigits

from .cpf_generator_options import CpfGeneratorOptions
from .exceptions import CpfGeneratorPrefixNotValidError


class CpfGenerator:
    """Class to generate a valid CPF according to the given options."""

    __slots__ = "_options"

    def __init__(self, format: bool | None = None, prefix: str | None = None):
        self._options = CpfGeneratorOptions(format, prefix)

    def generate(self, format: bool | None = None, prefix: str | None = None) -> str:
        """Executes the CPF generation, overriding any given options with the ones set on the generator instance."""
        actual_options = self._options.merge(format, prefix)

        prefix_numbers = [int(digit) for digit in actual_options.prefix]
        cpf_sequence = self._generate_id(prefix_numbers)

        try:
            CpfGeneratorOptions(prefix=cpf_sequence)
        except CpfGeneratorPrefixNotValidError:
            return self.generate(format, prefix)

        cpf_check_digits = CpfCheckDigits(cpf_sequence)
        cpf_generated = cpf_check_digits.to_string()

        if actual_options.format:
            return self._format(cpf_generated)

        return cpf_generated

    def _generate_id(self, prefix_numbers: list[int]) -> list[int]:
        id_length = 9

        id_start = prefix_numbers[:id_length]
        id_start_length = len(id_start)

        id_end = [random.randint(0, 9) for _ in range(id_length - id_start_length)]

        return id_start + id_end

    def _format(self, cpf_string: str) -> str:
        return (
            f"{cpf_string[0:3]}.{cpf_string[3:6]}.{cpf_string[6:9]}-{cpf_string[9:11]}"
        )

    @property
    def options(self) -> CpfGeneratorOptions:
        """Direct access to the options manager for the CPF generator."""
        return self._options
