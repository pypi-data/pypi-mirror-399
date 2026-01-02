from warnings import warn

from .cnpj_check_digits import CnpjCheckDigits
from .exceptions import (
    CnpjCheckDigitsCalculationError,
    CnpjCheckDigitsError,
    CnpjInvalidLengthError,
    CnpjTypeError,
)

__all__ = [
    "CnpjCheckDigits",
    "CnpjCheckDigitsCalculationError",
    "CnpjCheckDigitsError",
    "CnpjInvalidLengthError",
    "CnpjTypeError",
]

__version__ = "1.0.2"

warn(
    "This package is deprecated and will not receive further updates. Please use package: `cnpj-dv` instead.",
    DeprecationWarning,
    stacklevel=2,
)
