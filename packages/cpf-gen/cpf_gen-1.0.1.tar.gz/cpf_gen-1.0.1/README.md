![cpf-gen for Python](https://br-utils.vercel.app/img/cover_cpf-gen.jpg)

[![PyPI Version](https://img.shields.io/pypi/v/cpf-gen)](https://pypi.org/project/cpf-gen)
[![PyPI Downloads](https://img.shields.io/pypi/dm/cpf-gen)](https://pypi.org/project/cpf-gen)
[![Python Version](https://img.shields.io/pypi/pyversions/cpf-gen)](https://www.python.org/)
[![Test Status](https://img.shields.io/github/actions/workflow/status/LacusSolutions/br-utils-py/ci.yml?label=ci/cd)](https://github.com/LacusSolutions/br-utils-py/actions)
[![Last Update Date](https://img.shields.io/github/last-commit/LacusSolutions/br-utils-py)](https://github.com/LacusSolutions/br-utils-py)
[![Project License](https://img.shields.io/github/license/LacusSolutions/br-utils-py)](https://github.com/LacusSolutions/br-utils-py/blob/main/LICENSE)

Utility function/class to generate valid CPF (Brazilian personal ID).

## Python Support

| ![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white) | ![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) | ![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white) | ![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white) | ![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white) |
|--- | --- | --- | --- | --- |
| Passing ✔ | Passing ✔ | Passing ✔ | Passing ✔ | Passing ✔ |

## Installation

```bash
$ pip install cpf-gen
```

## Import

```python
# Using class-based resource
from cpf_gen import CpfGenerator

# Or using function-based one
from cpf_gen import cpf_gen
```

## Usage

### Object-Oriented Usage

```python
generator = CpfGenerator()
cpf = generator.generate()  # returns '47844241055'

# With options
cpf = generator.generate(
    format=True
)  # returns '478.442.410-55'

cpf = generator.generate(
    prefix='528250911'
)  # returns '52825091138'

cpf = generator.generate(
    prefix='528250911',
    format=True
)  # returns '528.250.911-38'
```

The options can be provided to the constructor or the `generate()` method. If passed to the constructor, the options will be attached to the `CpfGenerator` instance. When passed to the `generate()` method, it only applies the options to that specific call.

```python
generator = CpfGenerator(format=True)

cpf1 = generator.generate()  # '478.442.410-55' (uses instance options)
cpf2 = generator.generate(format=False)  # '47844241055' (overrides instance options)
cpf3 = generator.generate()  # '123.456.789-01' (uses instance options again)
```

### Functional programming

The helper function `cpf_gen()` is just a functional abstraction. Internally it creates an instance of `CpfGenerator` and calls the `generate()` method right away.

```python
cpf = cpf_gen()  # returns '47844241055'

cpf = cpf_gen(format=True)  # returns '478.442.410-55'

cpf = cpf_gen(prefix='528250911')  # returns '52825091138'

cpf = cpf_gen(prefix='528250911', format=True)  # returns '528.250.911-38'
```

### Generator Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | `bool \| None` | `False` | Whether to format the output with dots and dash |
| `prefix` | `str \| None` | `''` | If you have CPF initials and want to complete it with valid digits. The string provided must contain between 0 and 9 digits! |

## Error Handling

The package raises specific exceptions for different error scenarios:

### `CpfGeneratorPrefixLengthError`

Raised when the prefix length exceeds the maximum allowed (9 digits).

```python
from cpf_gen import CpfGenerator, CpfGeneratorPrefixLengthError

try:
    generator = CpfGenerator(prefix="1234567890") # 10 digits (too many)
except CpfGeneratorPrefixLengthError as e:
    print(e)  # The prefix length must be less than or equal to 9. Got 10.
```

### `CpfGeneratorPrefixNotValidError`

Raised when the input is forbidden for some restriction, like repeated digits like `111.111.111`, `222.222.222`, `333.333.333` and so on.

```python
from cpf_gen import CpfGenerator, CpfGeneratorPrefixNotValidError

try:
    generator = CpfGenerator(prefix="777777777")
except CpfGeneratorPrefixNotValidError as e:
    print(e)  # The prefix "777777777" is invalid. Repeated digits are not considered valid.
```

### Catch any error from the package

All errors extend from a common error instance `CpfGeneratorError`, so you can use this type to handle any error thrown by the module.

```python
from cpf_gen import CpfGeneratorError

try:
  # some risky code run
except CpfGeneratorError as e:
  # do something
```

## Features

- ✅ **Multiple Usage Patterns**: Supports both object-oriented and functional programming styles
- ✅ **Flexible Options**: Configure formatting and prefix at instance or method level
- ✅ **Valid CPF Generation**: Always generates CPFs with correct check digits
- ✅ **Type Safety**: Built with Python 3.10+ type hints
- ✅ **Zero Dependencies**: Only depends on `cpf-dv` for check digit calculation
- ✅ **Comprehensive Error Handling**: Specific exceptions for different error scenarios

## API Reference

### CpfGenerator Class

#### Constructor

```python
CpfGenerator(format: bool | None = None, prefix: str | None = None) -> CpfGenerator
```

Creates a new `CpfGenerator` instance with optional default options.

**Parameters:**
- `format` (bool | None): Whether to format the output with dots and dash. Defaults to `False`.
- `prefix` (str | None): CPF prefix (0-9 digits). Defaults to empty string.

**Returns:**
- `CpfGenerator`: A new instance ready to generate CPFs

#### Methods

##### `generate(format: bool | None = None, prefix: str | None = None) -> str`

Generates a valid CPF according to the given options.

**Parameters:**
- `format` (bool | None): Whether to format the output. If `None`, uses instance option.
- `prefix` (str | None): CPF prefix (0-9 digits). If `None`, uses instance option.

**Returns:**
- `str`: A valid CPF string (formatted or unformatted)

#### Properties

##### `options: CpfGeneratorOptions`

Direct access to the options manager for the CPF generator.

```python
generator = CpfGenerator()
generator.options.format = True
generator.options.prefix = "123456789"
```

### cpf_gen Function

```python
cpf_gen(format: bool | None = None, prefix: str | None = None) -> str
```

Functional wrapper that creates a `CpfGenerator` instance and calls `generate()` immediately.

**Parameters:**
- `format` (bool | None): Whether to format the output. Defaults to `False`.
- `prefix` (str | None): CPF prefix (0-9 digits). Defaults to empty string.

**Returns:**
- `str`: A valid CPF string (formatted or unformatted)

## Examples

```python
from cpf_gen import CpfGenerator, cpf_gen

# Basic usage
cpf1 = cpf_gen()  # '47844241055'
cpf2 = cpf_gen(format=True)  # '478.442.410-55'

# With prefix
cpf3 = cpf_gen(prefix='123456789')  # '12345678901'
cpf4 = cpf_gen(prefix='123456789', format=True)  # '123.456.789-01'

# Using class-based approach
generator = CpfGenerator(format=True)
cpf5 = generator.generate()  # '478.442.410-55'
cpf6 = generator.generate(format=False)  # '47844241055' (overrides instance option)

# Modify options directly
generator.options.prefix = "987654321"
cpf7 = generator.generate()  # '987.654.321-XX' (formatted with prefix)
```

## Dependencies

- **Python**: >= 3.10
- **cpf-dv**: for check digit calculation

## Contribution & Support

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/LacusSolutions/br-utils-py/blob/main/CONTRIBUTING.md) for details. But if you find this project helpful, please consider:

- ⭐ Starring the repository
- 🤝 Contributing to the codebase
- 💡 [Suggesting new features](https://github.com/LacusSolutions/br-utils-py/issues)
- 🐛 [Reporting bugs](https://github.com/LacusSolutions/br-utils-py/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/LacusSolutions/br-utils-py/blob/main/LICENSE) file for details.

## Changelog

See [CHANGELOG](https://github.com/LacusSolutions/br-utils-py/blob/main/packages/cpf-gen/CHANGELOG.md) for a list of changes and version history.

---

Made with ❤️ by [Lacus Solutions](https://github.com/LacusSolutions)
