"""Registry abstraction for Fragua.

This module contains the `FraguaRegistry` which holds named
`FraguaSet` instances. The registry is the primary discovery
mechanism for runtime components and is typically attached to
an environment instance.
"""

from typing import Any, Dict, Optional

from fragua.core.component import FraguaComponent
from fragua.core.set import FraguaSet


class FraguaRegistry(FraguaComponent):
    """
    Runtime registry within a Fragua environment.

    A `FraguaRegistry` manages a collection of `FraguaSet` instances,
    each representing a logical grouping of related components (e.g.
    agents, functions, internal helper specs). Registries are stateful
    and exist only at runtime; they provide a simple CRUD API for sets.

    Attributes
    ----------
    name:
        Inherited from `FraguaComponent`, the registry's logical name.
    _sets:
        Internal mapping of set_name -> FraguaSet.
    """

    def __init__(
        self,
        registry_name: str,
        sets: Optional[Dict[str, FraguaSet[Any]]] = None,
    ) -> None:
        """
        Initialize the registry with an optional pre-populated set mapping.

        Parameters
        ----------
        registry_name:
            Identifier used to reference this registry within the
            environment.
        sets:
            Optional mapping of initial FraguaSet instances.
        """
        super().__init__(instance_name=registry_name)

        # Internal storage of named sets (key: set_name)
        self._sets: Dict[str, FraguaSet[Any]] = sets if sets else {}

    def _exists(self, key: str) -> bool:
        """Return True if a set with `key` exists."""
        return key in self._sets

    def _not_exists(self, key: str) -> bool:
        """Return True when a set with `key` is not present."""
        return key not in self._sets

    def get_sets(self) -> Dict[str, FraguaSet[Any]]:
        """Retrieve all registered sets.

        Returns
        -------
        dict
            Mapping of set names to `FraguaSet` instances.
        """
        return self._sets

    def add_set(self, fragua_set: FraguaSet[Any]) -> bool:
        """Register a new `FraguaSet` under its `set_name`.

        Steps
        -----
        1. Check that the name is not already present.
        2. Insert the set into the registry.

        Returns
        -------
        bool
            True if the set was created, False if it already existed.
        """
        if self._not_exists(fragua_set.set_name):
            self._sets[fragua_set.set_name] = fragua_set
            return True
        return False

    def get_set(self, set_name: str) -> Optional[FraguaSet[Any]]:
        """Retrieve a set by its name. Returns None when not found."""
        return self._sets.get(set_name)

    def update_set(self, old_set_name: str, new_set_name: str) -> bool:
        """Rename an existing set in the registry.

        Returns True if rename succeeded, False otherwise.
        """
        if self._exists(old_set_name) and self._not_exists(new_set_name):
            self._sets[new_set_name] = self._sets.pop(old_set_name)
            return True
        return False

    def delete_set(self, set_name: str) -> bool:
        """Remove a set by name and return whether removal occurred."""
        return self._sets.pop(set_name, None) is not None

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the registry contents.

        The summary delegates to each contained `FraguaSet` to provide
        a structured view of their contents.
        """
        summary: Dict[str, Dict[str, Any]] = {}

        for set_name, fragua_set in self._sets.items():
            summary[set_name] = fragua_set.summary()

        return summary

    def __repr__(self) -> str:
        """Return a concise string representation of the registry."""
        return f"{self.__class__.__name__}('{self.name}')"
