from warnings import warn

from .cpf_check_digits import CpfCheckDigits
from .exceptions import (
    CpfCheckDigitsCalculationError,
    CpfCheckDigitsError,
    CpfCheckDigitsInputLengthError,
    CpfCheckDigitsInputNotValidError,
    CpfCheckDigitsInputTypeError,
)

__all__ = [
    "CpfCheckDigits",
    "CpfCheckDigitsCalculationError",
    "CpfCheckDigitsError",
    "CpfCheckDigitsInputLengthError",
    "CpfCheckDigitsInputNotValidError",
    "CpfCheckDigitsInputTypeError",
]

__version__ = "1.0.1"

warn(
    "This package is deprecated and will not receive further updates. Please use package: `cpf-dv` instead.",
    DeprecationWarning,
    stacklevel=2,
)
