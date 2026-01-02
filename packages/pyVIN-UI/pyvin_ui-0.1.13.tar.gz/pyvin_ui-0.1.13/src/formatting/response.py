from src.api.models import VINDecodeResult
from typing import Dict, Any


def filter_non_null(result: VINDecodeResult) -> Dict[str, Any]:
    """
    Return only non-null fields as a dict with field names (not aliases)

    This returns the Python field names (e.g., 'model_year') rather than
    the API aliases (e.g., 'ModelYear'), which allows for proper mapping
    to clean display labels.
    """
    return {
        k: v
        for k, v in result.model_dump(by_alias=False).items()
        if v is not None and v != ""
    }


__all__ = ["filter_non_null"]
