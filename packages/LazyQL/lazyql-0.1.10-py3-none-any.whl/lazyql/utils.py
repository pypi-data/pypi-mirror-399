from typing import Dict, Optional, Type
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
