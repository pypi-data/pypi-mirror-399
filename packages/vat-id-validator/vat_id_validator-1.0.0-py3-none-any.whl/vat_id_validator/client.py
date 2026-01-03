"""VAT ID Validator API Client."""

import os
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException

from .types import (
    HealthResponse,
    ValidateVatApproxRequest,
    ValidateVatApproxResponse,
    ValidateVatRequest,
    ValidateVatResponse,
)

# Default configuration
DEFAULT_BASE_URL = "https://vies-vat-validator.p.rapidapi.com"
DEFAULT_TIMEOUT = 10.0


class VatValidatorError(Exception):
    """Custom exception for VAT Validator API errors."""

    def __init__(self, message: str, status_code: int = 0, response: Optional[Any] = None):
        """
        Initialize VatValidatorError.

        Args:
            message: Error message
            status_code: HTTP status code (0 if not applicable)
            response: Raw response data
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class VatValidatorClient:
    """
    VAT ID Validator API Client.

    Examples:
        Basic usage:
        >>> client = VatValidatorClient(api_key="your-rapidapi-key")
        >>> result = client.validate_vat(country_code="IT", vat_number="00743110157")
        >>> if result["valid"]:
        ...     print(f"Valid VAT for: {result['name']}")

        Using environment variable:
        >>> client = VatValidatorClient()  # Reads RAPIDAPI_KEY from environment
        >>> result = client.validate_vat(country_code="DE", vat_number="169838187")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize VAT Validator client.

        Args:
            api_key: RapidAPI key (or use RAPIDAPI_KEY environment variable)
            base_url: Base URL for the API (default: https://vies-vat-validator.p.rapidapi.com)
            timeout: Request timeout in seconds (default: 10.0)

        Raises:
            ValueError: If no API key is provided via parameter or environment variable
        """
        # Get API key from parameter or environment
        self._api_key = api_key or os.environ.get("RAPIDAPI_KEY")

        if not self._api_key:
            raise ValueError(
                "API key is required. Provide it via api_key parameter "
                "or RAPIDAPI_KEY environment variable."
            )

        self._base_url = base_url or DEFAULT_BASE_URL
        self._timeout = timeout or DEFAULT_TIMEOUT

        # Create session for connection pooling
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-RapidAPI-Key": self._api_key,
                "Content-Type": "application/json",
            }
        )

    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key.

        Useful if you need to switch keys at runtime.

        Args:
            api_key: New RapidAPI key
        """
        self._api_key = api_key
        self._session.headers["X-RapidAPI-Key"] = api_key

    def set_base_url(self, base_url: str) -> None:
        """
        Update the base URL.

        Useful for testing or custom deployments.

        Args:
            base_url: New base URL
        """
        self._base_url = base_url

    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.

        Note: API key is masked for security.

        Returns:
            Dictionary with current configuration
        """
        return {
            "api_key": "***" + self._api_key[-4:] if len(self._api_key) >= 4 else "***",
            "base_url": self._base_url,
            "timeout": self._timeout,
        }

    def validate_vat(
        self,
        country_code: str,
        vat_number: str,
    ) -> ValidateVatResponse:
        """
        Validate a VAT number (basic validation).

        Args:
            country_code: 2-letter ISO country code (e.g., 'DE', 'IT', 'FR')
            vat_number: VAT number without country prefix

        Returns:
            Validation result with company details if valid

        Raises:
            VatValidatorError: If the API request fails

        Examples:
            >>> client = VatValidatorClient(api_key="your-key")
            >>> result = client.validate_vat(country_code="DE", vat_number="169838187")
            >>> print(result["valid"])
            True
        """
        try:
            response = self._session.get(
                f"{self._base_url}/validate-vat",
                params={
                    "countryCode": country_code,
                    "vatNumber": vat_number,
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise self._handle_error(e)

    def validate_vat_approx(
        self,
        country_code: str,
        vat_number: str,
        trader_name: Optional[str] = None,
        trader_street: Optional[str] = None,
        trader_postal_code: Optional[str] = None,
        trader_city: Optional[str] = None,
        requester_country_code: Optional[str] = None,
        requester_vat_number: Optional[str] = None,
    ) -> ValidateVatApproxResponse:
        """
        Validate a VAT number with approximate matching (advanced validation).

        Args:
            country_code: 2-letter ISO country code
            vat_number: VAT number without country prefix
            trader_name: Company name for approximate matching
            trader_street: Street address for approximate matching
            trader_postal_code: Postal code for approximate matching
            trader_city: City for approximate matching
            requester_country_code: Country code of the requester (your company)
            requester_vat_number: VAT number of the requester (your company)

        Returns:
            Validation result with matched trader information

        Raises:
            VatValidatorError: If the API request fails

        Examples:
            >>> client = VatValidatorClient(api_key="your-key")
            >>> result = client.validate_vat_approx(
            ...     country_code="DE",
            ...     vat_number="169838187",
            ...     trader_name="Google Germany",
            ...     trader_city="Berlin"
            ... )
        """
        params: Dict[str, str] = {
            "countryCode": country_code,
            "vatNumber": vat_number,
        }

        # Add optional parameters if provided
        if trader_name:
            params["traderName"] = trader_name
        if trader_street:
            params["traderStreet"] = trader_street
        if trader_postal_code:
            params["traderPostalCode"] = trader_postal_code
        if trader_city:
            params["traderCity"] = trader_city
        if requester_country_code:
            params["requesterCountryCode"] = requester_country_code
        if requester_vat_number:
            params["requesterVatNumber"] = requester_vat_number

        try:
            response = self._session.get(
                f"{self._base_url}/validate-vat-approx",
                params=params,
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise self._handle_error(e)

    def health(self) -> HealthResponse:
        """
        Check API health status.

        This endpoint does not require authentication.

        Returns:
            Health status

        Raises:
            VatValidatorError: If the API request fails

        Examples:
            >>> client = VatValidatorClient(api_key="your-key")
            >>> health = client.health()
            >>> print(health["status"])
            'healthy'
        """
        try:
            response = self._session.get(
                f"{self._base_url}/health",
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise self._handle_error(e)

    def _handle_error(self, error: RequestException) -> VatValidatorError:
        """
        Handle requests errors and convert to VatValidatorError.

        Args:
            error: RequestException from requests library

        Returns:
            VatValidatorError with appropriate message and status code
        """
        if hasattr(error, "response") and error.response is not None:
            # Server responded with error
            try:
                error_data = error.response.json()
                message = error_data.get("error", str(error))
            except Exception:
                message = str(error)

            return VatValidatorError(
                message=message,
                status_code=error.response.status_code,
                response=error.response.text,
            )
        else:
            # Request made but no response (network error, timeout, etc.)
            return VatValidatorError(
                message="No response from server. Please check your network connection.",
                status_code=0,
                response=None,
            )

    def __enter__(self) -> "VatValidatorClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the session and release resources."""
        self._session.close()
