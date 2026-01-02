class VINDecoderError(Exception):
    """Base exception for VIN decoder"""

    pass


class InvalidVINError(VINDecoderError):
    """VIN failed validation"""

    pass


class APIError(VINDecoderError):
    """NHTSA API returned an error"""

    pass


class NetworkError(VINDecoderError):
    """Network/connection error"""

    pass


__all__ = [
    "VINDecoderError",
    "InvalidVINError",
    "APIError",
    "NetworkError",
]
