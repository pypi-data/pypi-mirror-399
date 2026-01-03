from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type
from strawberry.types import Info
from pydantic import BaseModel


def get_mongo_projection(
    info: Info, model: Type[BaseModel]
) -> Optional[Dict[str, int]]:
    """
    Extract MongoDB projection from GraphQL query selection.

    Returns None if projection cannot be determined or if all fields
    should be returned.
    """
    if not hasattr(info, "selected_fields") or not info.selected_fields:
        return None

    projection = {}

    try:
        # Handle case where selected_fields might not be indexable
        if not isinstance(info.selected_fields, (list, tuple)):
            return None

        if len(info.selected_fields) == 0:
            return None

        root_field = info.selected_fields[0]
        if not hasattr(root_field, "selections"):
            return None

        for selection in root_field.selections:
            if hasattr(selection, "name") and not selection.name.startswith("__"):
                projection[selection.name] = 1
    except (IndexError, AttributeError, TypeError):
        return None

    if not projection:
        return None

    for name, field in model.model_fields.items():
        if field.is_required():
            key = field.alias or name
            projection[key] = 1

    return projection


def normalize_datetime_to_utc(value: Any) -> Any:
    """
    Normalize datetime objects to UTC (naive) for MongoDB compatibility.

    Converts all timezone-aware datetime objects to UTC and removes timezone info.
    MongoDB stores dates in UTC without timezone info, so we normalize all
    timezone-aware datetimes to UTC.

    Handles:
    - Single datetime values
    - Lists containing datetimes
    - Dictionaries with datetime values (recursive)
    - Nested structures

    Args:
        value: Value to normalize (can be datetime, list, dict, or any other type)

    Returns:
        Normalized value with all datetimes converted to UTC (naive)
    """
    if isinstance(value, datetime):
        # Convert to UTC if timezone-aware, otherwise assume already UTC
        if value.tzinfo is not None:
            # Convert to UTC and remove timezone info (naive UTC)
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        # Already naive, assume UTC (MongoDB standard)
        return value

    if isinstance(value, list):
        return [normalize_datetime_to_utc(v) for v in value]

    if isinstance(value, dict):
        return {k: normalize_datetime_to_utc(v) for k, v in value.items()}

    return value
