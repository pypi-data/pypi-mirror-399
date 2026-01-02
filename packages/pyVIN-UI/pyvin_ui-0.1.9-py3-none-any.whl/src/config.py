"""Configuration constants for the VIN decoder application."""

from typing import Final

NHTSA_BASE_URL: Final[str] = "https://vpic.nhtsa.dot.gov/api/vehicles"
DECODE_VIN_EXT_ENDPOINT: Final[str] = "DecodeVinValuesExtended"
DEFAULT_FORMAT: Final[str] = "json"
REQUEST_TIMEOUT: Final[int] = 10
CACHE_SIZE: Final[int] = 256

__all__ = [
    "NHTSA_BASE_URL",
    "DECODE_VIN_EXT_ENDPOINT",
    "DEFAULT_FORMAT",
    "REQUEST_TIMEOUT",
    "CACHE_SIZE",
]
