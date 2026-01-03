"""Metadata utilities for Fragua."""

from typing import Any, Dict, Optional
from fragua.utils.metrics.metrics import calculate_checksum, get_local_time_and_offset
from fragua.utils.logger import get_logger
from fragua.utils.types.enums import AttrType, ComponentType, FieldType, MetadataType

logger = get_logger(__name__)


def generate_metadata(
    storage: Any,
    **metadata_kwargs: Any,
) -> Dict[str, Any]:
    """
    Generate metadata dictionary for objects with .data and .name.

    Args:
        storage: Storage object that holds data (e.g., Box, Container).
        **metadata_kwargs: Additional metadata fields
            (e.g., metadata_type, storage_name, agent_name, function_name, etc.).
    """
    data_attr = getattr(storage, FieldType.DATA.value, storage)
    rows, columns = getattr(data_attr, "shape", (None, None))
    checksum = calculate_checksum(data_attr)
    local_time, timezone_offset = get_local_time_and_offset()

    base_metadata: dict[str, Any] = {
        MetadataType.LOCA_TIME.value: local_time,
        MetadataType.TIMEZONE_OFFSET.value: timezone_offset,
        MetadataType.ROWS.value: rows,
        MetadataType.COLS.value: columns,
        "base_checksum": checksum,
    }

    class_type = storage.__class__.__name__.lower()

    metadata_type = metadata_kwargs.get(MetadataType.METADATA_TYPE.value)

    if metadata_type == MetadataType.BASE.value:
        base_metadata.update({AttrType.TYPE.value: class_type})

    elif metadata_type == MetadataType.OPERATION.value:
        base_metadata.update(
            {
                ComponentType.FUNCTION.value: metadata_kwargs.get(
                    ComponentType.FUNCTION.value
                ),
                "operation_checksum": checksum,
            }
        )

    elif metadata_type == MetadataType.SAVE.value:
        base_metadata.update(
            {
                ComponentType.STORAGE.value: metadata_kwargs.get(
                    ComponentType.STORAGE.value
                ),
                ComponentType.AGENT.value: metadata_kwargs.get(
                    ComponentType.AGENT.value
                ),
                "save_checksum": checksum,
            }
        )

    else:
        raise ValueError(f"Unknown metadata_type '{metadata_type}'")

    return base_metadata


def add_metadata_to_storage(
    storage: Any,
    metadata: Optional[dict[str, object]] = None,
) -> None:
    """
    Add or merge metadata into a unified metadata dictionary of a storage object.

    Args:
        storage (Storage): The target storage object (e.g., Box, Container).
        data (dict | None): Metadata to add.

    Notes:
        - Automatically ignores None or empty data.
        - Merges keys recursively (non-destructive).
    """
    if not metadata:
        logger.debug("[%s] No metadata provided.", storage.name)
        return

    if not hasattr(storage, "metadata") or storage.metadata is None:
        storage.metadata = {}

    storage.metadata.update(metadata)
