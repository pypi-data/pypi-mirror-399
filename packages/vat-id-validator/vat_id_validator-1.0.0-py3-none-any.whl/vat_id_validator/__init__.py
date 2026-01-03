"""
VAT ID Validator - Python Client

Official Python client for the VAT ID Validator API.
Validate EU VAT numbers using the VIES database.
"""

from .client import VatValidatorClient, VatValidatorError
from .types import (
    ValidateVatRequest,
    ValidateVatResponse,
    ValidateVatApproxRequest,
    ValidateVatApproxResponse,
    HealthResponse,
)

__version__ = "1.0.0"
__all__ = [
    "VatValidatorClient",
    "VatValidatorError",
    "ValidateVatRequest",
    "ValidateVatResponse",
    "ValidateVatApproxRequest",
    "ValidateVatApproxResponse",
    "HealthResponse",
]
