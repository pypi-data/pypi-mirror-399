"""Fragua Registry Class."""

from typing import Any, Dict, Optional

from fragua.core.component import FraguaComponent
from fragua.core.set import FraguaSet


class FraguaRegistry(FraguaComponent):
    """
    Runtime registry within a Fragua environment.

    A FraguaRegistry manages a collection of FraguaSet instances,
    each representing a logical grouping of related components
    (such as agents, functions, etc).

    Registries are stateful and exist only at runtime.
    """

    def __init__(
        self,
        registry_name: str,
        sets: Optional[Dict[str, FraguaSet[Any]]] = None,
    ) -> None:
        """
        Initialize the registry with a name.

        Args:
            registry_name:
                Identifier used to reference this registry
                within the environment.
        """
        super().__init__(instance_name=registry_name)

        self._sets: Dict[str, FraguaSet[Any]] = sets if sets else {}

    def _exists(self, key: str) -> bool:
        """Return True if a set exists in the registry."""
        return key in self._sets

    def _not_exists(self, key: str) -> bool:
        """Return True if a set does not exist in the registry."""
        return key not in self._sets

    def get_sets(self) -> Dict[str, FraguaSet[Any]]:
        """
        Retrieve all registered sets.

        Returns:
            A mapping of set names to FraguaSet instances.
        """
        return self._sets

    def add_set(self, fragua_set: FraguaSet[Any]) -> bool:
        """
        Register a new FraguaSet.

        Returns:
            True if created successfully, False if already exists.
        """
        if self._not_exists(fragua_set.set_name):
            self._sets[fragua_set.set_name] = fragua_set
            return True
        return False

    def get_set(self, set_name: str) -> Optional[FraguaSet[Any]]:
        """
        Retrieve a set by name.
        """
        return self._sets.get(set_name)

    def update_set(self, old_set_name: str, new_set_name: str) -> bool:
        """
        Rename an existing set.
        """
        if self._exists(old_set_name) and self._not_exists(new_set_name):
            self._sets[new_set_name] = self._sets.pop(old_set_name)
            return True
        return False

    def delete_set(self, set_name: str) -> bool:
        """
        Remove a set from the registry.
        """
        return self._sets.pop(set_name, None) is not None

    def summary(self) -> Dict[str, Any]:
        """
        Return a summary of the registry contents.
        Returns:
            A dictionary summarizing the contents of each set.

        """
        summary: Dict[str, Dict[str, Any]] = {}

        for set_name, fragua_set in self._sets.items():
            summary[set_name] = fragua_set.summary()

        return summary

    def __repr__(self) -> str:
        """
        Return a concise string representation of the registry.
        """
        return f"{self.__class__.__name__}('{self.name}')"
