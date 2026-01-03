"""
Base storage class for all storage objects in Fragua (Wagon, Box, Container).
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
    Core runtime storage abstraction for all persistable objects in Fragua.
    """

    def __init__(self, storage_name: str, data: Optional[T] = None) -> None:
        super().__init__(instance_name=storage_name)
        self._data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        if data is not None:
            self._generate_base_metadata()

    @property
    def data(self) -> Optional[T]:
        """Access the stored data."""
        return self._data

    def _generate_base_metadata(self) -> None:
        """
        Generate and attach base metadata to the storage.

        Base metadata typically includes information such as storage type,
        creation context, and timestamps.
        """
        metadata = generate_metadata(self, metadata_type=MetadataType.BASE.value)
        add_metadata_to_storage(self, metadata)

    def summary(self) -> Dict[str, Any]:
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
    """

    def __init__(
        self,
        storage_name: str,
        data: pd.DataFrame | None = None,
    ) -> None:
        super().__init__(storage_name=storage_name, data=None)

        if data is not None:
            self.set(data)

    def set(self, data: pd.DataFrame) -> None:
        """Set box data."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                f"Box requires a pandas DataFrame, got {type(data).__name__}"
            )
        self._data = data
        self._generate_base_metadata()


STORAGE_CLASSES: dict[str, type[Storage[Any]]] = {
    StorageType.BOX.value: Box,
}
