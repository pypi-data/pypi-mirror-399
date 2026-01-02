from .cpf_generator import CpfGenerator


def cpf_gen(format: bool | None = None, prefix: str | None = None) -> str:
    """Generate a valid CPF according to the given options."""
    generator = CpfGenerator(format, prefix)

    return generator.generate()
