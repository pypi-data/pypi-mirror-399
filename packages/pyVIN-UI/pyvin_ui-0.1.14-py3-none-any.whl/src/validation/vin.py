import re
from src.exceptions import InvalidVINError

VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9*]{17}$")  # * allowed for wildcards


def validate_and_normalize_vin(vin: str) -> str:
    """
    Validate and normalize VIN. Returns uppercase VIN.

    Requires exactly 17 characters. Use * as wildcard for unknown positions.

    Args:
        vin: VIN string to validate (must be 17 characters)

    Returns:
        Normalized (uppercase, stripped) VIN

    Raises:
        InvalidVINError: If VIN format is invalid
    """
    if not vin:
        raise InvalidVINError("VIN cannot be empty")

    normalized = vin.upper().strip()

    if not normalized:
        raise InvalidVINError("VIN cannot be empty")

    # Regex handles both length (exactly 17) and valid characters
    if not VIN_PATTERN.match(normalized):
        # Figure out if it's length or character issue for better error message
        if len(normalized) != 17:
            raise InvalidVINError(
                f"VIN must be exactly 17 characters (got {len(normalized)}). "
                "Use * as wildcard for unknown positions."
            )
        else:
            raise InvalidVINError(
                f"Invalid VIN format: {vin}. "
                "Only A-Z, 0-9, and * allowed. Letters I, O, and Q are not valid."
            )

    return normalized


__all__ = ["validate_and_normalize_vin", "VIN_PATTERN"]
