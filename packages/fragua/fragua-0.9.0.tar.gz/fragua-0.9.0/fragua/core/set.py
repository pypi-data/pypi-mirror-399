"""Fragua set utilities.

This module exposes `FraguaSet`, an abstract container used to manage
homogeneous collections of runtime elements (for example: functions
or agents). The class provides convenience helpers to add, retrieve,
rename and remove entries and to produce human-friendly summaries
suitable for logs, admin UIs or debugging output.
"""

from abc import ABC
from typing import Any, Dict, Generic, Optional, TypeVar
from dataclasses import is_dataclass

from fragua.core.component import FraguaComponent

T = TypeVar("T")


class FraguaSet(ABC, Generic[T]):
    """
    Logical container for Fragua components.

    A FraguaSet groups homogeneous elements under a common scope
    (functions, agents, etc.). Implementations store elements in an
    internal mapping keyed by the element name.
    """

    def __init__(
        self,
        set_name: str,
        *,
        components: Optional[Dict[str, T]] = None,
    ) -> None:
        """
        Initialize the set.

        Parameters
        ----------
        set_name:
            Identifier of the set within its parent registry.
        components:
            Optional preloaded elements.
        """
        self.set_name = set_name
        # Internal storage mapping for items in the set
        self._components: Dict[str, T] = {} if components is None else components

    def _exists(self, key: str) -> bool:
        """Return True if the element exists in the set."""
        return key in self._components

    def _not_exists(self, key: str) -> bool:
        """Return True if the element does not exist in the set."""
        return key not in self._components

    def add(self, name: str, component: T) -> bool:
        """Add a new element to the set.

        Steps:
        1. Check the name is not already present.
        2. Insert the element into the internal mapping.

        Returns ``True`` when added successfully, ``False`` when the name
        is already taken.
        """
        # 1) Ensure the name is available
        if self._not_exists(name):
            # 2) Insert the component
            self._components[name] = component
            return True
        return False

    def get_one(self, name: str) -> Optional[T]:
        """Retrieve a single element by name.

        Returns the element or ``None`` if it is not present.
        """
        # Direct dictionary lookup; callers validate presence as needed
        return self._components.get(name)

    def get_all(self) -> Dict[str, T]:
        """Return the full mapping of elements in this set."""
        return self._components

    def update_one(self, old_name: str, new_name: str) -> bool:
        """Rename an element within the set.

        Steps:
        1. Verify the old name exists and the new name is free.
        2. Move the stored element to the new key.
        3. Return ``True`` on success, ``False`` otherwise.
        """
        if self._exists(old_name) and self._not_exists(new_name):
            self._components[new_name] = self._components.pop(old_name)
            return True
        return False

    def delete_one(self, name: str) -> bool:
        """Remove an element from the set.

        Returns ``True`` if removal happened, ``False`` if the element
        was not present.
        """
        return self._components.pop(name, None) is not None

    def summary(self) -> Dict[str, Any]:
        """Return a structured summary of the set contents.

        The summary attempts to provide human-friendly representations for
        elements based on their type: Fragua components delegate to their
        own `summary()` implementation; mapping-like function records are
        summarized recursively; dataclass-based specs are inspected for
        user-facing fields; callables are represented by name; and a
        fallback string is used for unknown types.
        """

        result: Dict[str, Any] = {}

        for name, component in self._components.items():
            # 1) If it's a FraguaComponent, use its own summary()
            if isinstance(component, FraguaComponent):
                result[name] = component.summary()

            # 2) If it's a mapping-like record (common for function specs),
            #    summarize each nested value in a readable way.
            elif isinstance(component, dict):
                nested: Dict[str, Any] = {}
                for key, value in component.items():
                    # nested components keep their own summaries
                    if isinstance(value, FraguaComponent):
                        nested[key] = value.summary()
                    # dataclass specs inside dict are summarized using
                    # _summarize_spec to pick relevant metadata fields
                    elif is_dataclass(value):
                        nested[key] = self._summarize_spec(value)
                    # plain callables are represented by their __name__
                    elif callable(value):
                        nested[key] = getattr(value, "__name__", repr(value))
                    else:
                        nested[key] = value
                result[name] = nested

            # 3) dataclass-based specs (TransformInternalSpec, LoadInternalSpec)
            elif is_dataclass(component):
                result[name] = self._summarize_spec(component)

            # 4) Callables are represented by name
            elif callable(component):
                result[name] = getattr(
                    component, "__name__", component.__class__.__name__
                )

            # 5) Fallback: include the type name for unknown objects
            else:
                result[name] = component.__class__.__name__

        return result

    def _summarize_spec(self, spec: object) -> Dict[str, Any]:
        """Extract friendly summary from an internal spec dataclass object.

        The helper picks well-known fields (purpose/description, config_keys)
        and emits a `function` entry when the spec contains a callable.
        """
        summary: Dict[str, Any] = {}

        # common fields
        if hasattr(spec, "purpose"):
            summary["purpose"] = getattr(spec, "purpose")
        if hasattr(spec, "description"):
            summary["description"] = getattr(spec, "description")
        if hasattr(spec, "config_keys"):
            summary["config_keys"] = list(getattr(spec, "config_keys") or [])

        # optional fields
        if hasattr(spec, "data_arg"):
            summary["data_arg"] = getattr(spec, "data_arg")

        # function name
        func = getattr(spec, "func", None)
        if callable(func):
            summary["function"] = getattr(func, "__name__", repr(func))

        return summary
