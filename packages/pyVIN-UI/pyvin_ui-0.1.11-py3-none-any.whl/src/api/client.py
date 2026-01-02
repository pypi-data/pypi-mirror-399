from functools import lru_cache
import requests
from api.models import VINDecodeResult
from config import (
    CACHE_SIZE,
    DECODE_VIN_EXT_ENDPOINT,
    DEFAULT_FORMAT,
    NHTSA_BASE_URL,
    REQUEST_TIMEOUT,
)
from exceptions import APIError, NetworkError
from validation.vin import validate_and_normalize_vin


@lru_cache(maxsize=CACHE_SIZE)
def decode_vin_values_extended(vin: str) -> VINDecodeResult:
    """
    Decode VIN using NHTSA API. Returns Pydantic model.

    The NHTSA API returns error codes that can be warnings or errors:
    - Error codes 0-99: Informational/warnings (e.g., check digit issues, partial data)
    - Error codes 400+: Critical errors (invalid characters, format issues)

    This function returns results for warnings but raises APIError for critical errors.
    Check result.error_text and result.suggested_vin for additional information.

    Args:
        vin: 17-character VIN (use * for wildcards)

    Returns:
        VINDecodeResult with decoded data (may include warnings in error_text)

    Raises:
        InvalidVINError: VIN format is invalid
        NetworkError: Network/connection error
        APIError: Critical API error (400+ error codes)
    """
    normalized_vin = validate_and_normalize_vin(vin)

    url = f"{NHTSA_BASE_URL}/{DECODE_VIN_EXT_ENDPOINT}/{normalized_vin}"
    params = {"format": DEFAULT_FORMAT}

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise NetworkError(f"Failed to reach NHTSA API: {e}")

    data = resp.json()

    if not data.get("Results"):
        raise APIError("No results returned from API")

    result = VINDecodeResult(**data["Results"][0])

    # Only raise error for critical errors (400+), not warnings (0-99)
    if result.error_code:
        try:
            error_code_int = int(
                result.error_code.split()[0].split(",")[0]
            )  # Handle "1,11,14" format
            if error_code_int >= 400:
                # Critical error - raise exception
                msg = f"API Error: {result.error_text}"
                if result.suggested_vin:
                    msg += f"\nSuggested VIN: {result.suggested_vin}"
                if result.possible_values:
                    msg += f"\nPossible values: {result.possible_values}"
                raise APIError(msg)
            # else: warning codes (0-99) - return result with warnings in error_text
        except (ValueError, AttributeError):
            # If we can't parse error code, treat error_code "0" as success
            if result.error_code != "0":
                # Unknown error format - raise to be safe
                raise APIError(f"API Error: {result.error_text}")

    return result
