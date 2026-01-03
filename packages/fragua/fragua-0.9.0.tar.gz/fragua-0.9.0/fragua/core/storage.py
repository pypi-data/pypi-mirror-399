"""Storage abstractions used by Fragua.

This module defines the base `Storage` abstraction and concrete
implementations such as `Box`. Storages are lightweight containers
that hold data produced by agents and allow metadata to be attached
via the metrics utilities.
"""

from typing import Any, Dict, Generic, Optional, TypeVar
import pandas as pd
from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata
from fragua.utils.types.enums import AttrType, ComponentType, MetadataType, StorageType

T = TypeVar("T")

logger = get_logger(__name__)


class Storage(FraguaComponent, Generic[T]):
    """
    Core runtime storage abstraction for persistable objects.

    The `Storage` class encapsulates stored data together with optional
    metadata. Subclasses are responsible for enforcing data invariants
    (for example, `Box` requires a pandas DataFrame).

    Attributes
    ----------
    _data: Optional[T]
        The actual payload stored in this Storage instance.
    _metadata: dict
        Metadata dictionary populated by `generate_metadata` utilities.
    """

    def __init__(self, storage_name: str, data: Optional[T] = None) -> None:
        # Initialize component base (name, etc.) and internal state
        super().__init__(instance_name=storage_name)
        self._data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        # If we are initialized with content, generate base metadata
        if data is not None:
            self._generate_base_metadata()

    @property
    def data(self) -> Optional[T]:
        """Return the stored payload (or ``None`` if empty)."""
        return self._data

    def _generate_base_metadata(self) -> None:
        """Generate and attach base metadata for this storage.

        Steps:
        1. Generate metadata using the project's metrics helpers.
        2. Attach the metadata record to the storage instance.
        """
        metadata = generate_metadata(self, metadata_type=MetadataType.BASE.value)
        add_metadata_to_storage(self, metadata)

    def summary(self) -> Dict[str, Any]:
        """Return a compact summary of the storage instance."""
        return {
            AttrType.TYPE.value: ComponentType.STORAGE.value,
            AttrType.NAME.value: self.name,
            AttrType.CLASS.value: self.__class__.__name__,
            "has_data": self._data is not None,
            "metadata_keys": list(self._metadata.keys()),
        }


class Box(Storage[pd.DataFrame]):
    """
    Storage type representing a single unit of tabular data.

    `Box` enforces that its payload is a pandas DataFrame and regenerates
    base metadata when the data is set.
    """

    def __init__(
        self,
        storage_name: str,
        data: pd.DataFrame | None = None,
    ) -> None:
        # Initialize without data to allow validation in `set()`
        super().__init__(storage_name=storage_name, data=None)

        # Optionally set validated data at construction time
        if data is not None:
            self.set(data)

    def set(self, data: pd.DataFrame) -> None:
        """Validate and set the Box payload.

        Raises
        ------
        TypeError
            If the provided payload is not a pandas DataFrame.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                f"Box requires a pandas DataFrame, got {type(data).__name__}"
            )
        # Store data and update base metadata to reflect creation time
        self._data = data
        self._generate_base_metadata()


# Mapping used by agents to select appropriate storage class by storage type
STORAGE_CLASSES: dict[str, type[Storage[Any]]] = {
    StorageType.BOX.value: Box,
}
