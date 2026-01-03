"""Type definitions for VAT ID Validator API."""

from typing import Optional, TypedDict


class ValidateVatRequest(TypedDict):
    """Request parameters for basic VAT validation."""

    country_code: str
    """2-letter ISO country code (e.g., 'DE', 'IT', 'FR')"""

    vat_number: str
    """VAT number without country prefix"""


class ValidateVatResponse(TypedDict):
    """Response from basic VAT validation."""

    countryCode: str
    """ISO country code"""

    vatNumber: str
    """VAT number that was validated"""

    requestDate: str
    """ISO 8601 timestamp of the validation request"""

    valid: bool
    """Whether the VAT number is valid"""

    name: Optional[str]
    """Registered company name (only if valid and available)"""

    address: Optional[str]
    """Registered business address (only if valid and available)"""


class ValidateVatApproxRequest(TypedDict, total=False):
    """Request parameters for approximate VAT validation with trader details."""

    country_code: str
    """2-letter ISO country code (e.g., 'DE', 'IT', 'FR')"""

    vat_number: str
    """VAT number without country prefix"""

    trader_name: Optional[str]
    """Company name for approximate matching"""

    trader_street: Optional[str]
    """Street address for approximate matching"""

    trader_postal_code: Optional[str]
    """Postal code for approximate matching"""

    trader_city: Optional[str]
    """City for approximate matching"""

    requester_country_code: Optional[str]
    """Country code of the requester (your company)"""

    requester_vat_number: Optional[str]
    """VAT number of the requester (your company)"""


class ValidateVatApproxResponse(TypedDict):
    """Response from approximate VAT validation."""

    countryCode: str
    """ISO country code"""

    vatNumber: str
    """VAT number that was validated"""

    requestDate: str
    """ISO 8601 timestamp of the validation request"""

    valid: bool
    """Whether the VAT number is valid"""

    traderName: Optional[str]
    """Registered trader/company name from VIES"""

    traderStreet: Optional[str]
    """Registered street address from VIES"""

    traderPostalCode: Optional[str]
    """Registered postal code from VIES"""

    traderCity: Optional[str]
    """Registered city from VIES"""


class HealthResponse(TypedDict):
    """Health check response."""

    status: str
    """Health status (e.g., 'healthy')"""


class ApiError(TypedDict):
    """Error response from the API."""

    error: str
    """Error description"""
