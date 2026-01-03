"""Example usage of VAT ID Validator Python client."""

import os
from vat_id_validator import VatValidatorClient, VatValidatorError


def main():
    """Run example validations."""
    # Initialize client (reads RAPIDAPI_KEY from environment)
    api_key = os.environ.get("RAPIDAPI_KEY", "your-api-key-here")
    
    # For local testing, you can use:
    # client = VatValidatorClient(api_key=api_key, base_url="http://localhost:8787")
    
    with VatValidatorClient(api_key=api_key) as client:
        try:
            # Check API health
            print("Checking API health...")
            health = client.health()
            print(f"Health: {health}")

            # Validate Italian VAT number
            print("\nValidating Italian VAT number...")
            result = client.validate_vat(
                country_code="IT",
                vat_number="00743110157"
            )

            print(f"Result: {result}")
            print(f"Valid: {result['valid']}")
            if result["valid"]:
                print(f"Company: {result.get('name')}")
                print(f"Address: {result.get('address')}")

            # Validate with approximate matching
            print("\nValidating with trader details...")
            approx_result = client.validate_vat_approx(
                country_code="IT",
                vat_number="00743110157",
                trader_name="Motorola Solutions",
                trader_city="Milano"
            )

            print(f"Approx Result: {approx_result}")

            # Batch validation example
            print("\nBatch validation example...")
            vat_numbers = [
                {"country_code": "IT", "vat_number": "00743110157"},
                {"country_code": "DE", "vat_number": "169838187"},
            ]

            for vat in vat_numbers:
                try:
                    result = client.validate_vat(**vat)
                    status = "✓" if result["valid"] else "✗"
                    company = result.get("name", "Unknown")
                    print(f"{vat['country_code']}{vat['vat_number']}: {status} - {company}")
                except VatValidatorError as e:
                    print(f"{vat['country_code']}{vat['vat_number']}: Error - {e}")

        except VatValidatorError as e:
            print(f"Error: {e}")
            if e.status_code:
                print(f"Status Code: {e.status_code}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
