"""
Fragua Set class.
"""

from abc import ABC
from typing import Any, Dict, Generic, Optional, TypeVar

from fragua.core.component import FraguaComponent

T = TypeVar("T")


class FraguaSet(ABC, Generic[T]):
    """
    Logical container for Fragua components.

    A FraguaSet groups homogeneous elements under a common scope
    (functions, agents, etc.).
    """

    def __init__(
        self,
        set_name: str,
        *,
        components: Optional[Dict[str, T]] = None,
    ) -> None:
        """
        Initialize the set.

        Args:
            set_name:
                Identifier of the set within its parent registry.
            components:
                Optional preloaded elements.
        """
        self.set_name = set_name
        self._components: Dict[str, T] = {} if components is None else components

    def _exists(self, key: str) -> bool:
        return key in self._components

    def _not_exists(self, key: str) -> bool:
        return key not in self._components

    def add(self, name: str, component: T) -> bool:
        """
        Add a new element to the set.
        """
        if self._not_exists(name):
            self._components[name] = component
            return True
        return False

    def get_one(self, name: str) -> Optional[T]:
        """
        Retrieve a single element by name.

        Args:
            name: Name of the element.

        Returns:
            The element if found, otherwise None.
        """
        return self._components.get(name)

    def get_all(self) -> Dict[str, T]:
        """
        Retrieve all elements in the set.

        Returns:
            A dictionary mapping element names to elements.
        """
        return self._components

    def update(self, old_name: str, new_name: str) -> bool:
        """
        Rename an element within the set.

        Args:
            old_name: Current element name.
            new_name: New element name.

        Returns:
            True if the element was renamed successfully, False if the
            old name does not exist or the new name is already in use.
        """
        if self._exists(old_name) and self._not_exists(new_name):
            self._components[new_name] = self._components.pop(old_name)
            return True
        return False

    def delete_one(self, name: str) -> bool:
        """
        Remove an element from the set.

        Args:
            name: Name of the element to delete.

        Returns:
            True if the element was removed, False if it did not exist.
        """
        return self._components.pop(name, None) is not None

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the set contents.

        Delegates summary generation to the contained elements
        according to the declared content kind. Internal helper specs
        (frozen dataclasses used for internal functions) are summarized
        with their metadata (purpose/description, config_keys, etc.)
        instead of their Python types.
        """
        from dataclasses import is_dataclass

        result: Dict[str, Any] = {}

        for name, component in self._components.items():
            # Fragua components delegate to their own summary
            if isinstance(component, FraguaComponent):
                result[name] = component.summary()

            # Standard mapping-like records (functions set entries)
            elif isinstance(component, dict):
                nested: Dict[str, Any] = {}
                for key, value in component.items():
                    # nested components keep their own summaries
                    if isinstance(value, FraguaComponent):
                        nested[key] = value.summary()
                    # dataclass specs inside dict (rare) are summarized
                    elif is_dataclass(value):
                        # pick well-known fields when present
                        nested[key] = self._summarize_spec(value)
                    elif callable(value):
                        nested[key] = value.__name__
                    else:
                        nested[key] = value
                result[name] = nested

            # dataclass-based specs (TransformInternalSpec, LoadInternalSpec)
            elif is_dataclass(component):
                result[name] = self._summarize_spec(component)

            # Callables are represented by name
            elif callable(component):
                # Use getattr to satisfy static type checkers: callables may not have __name__
                result[name] = getattr(
                    component, "__name__", component.__class__.__name__
                )

            # Fallback: show simple type name
            else:
                result[name] = component.__class__.__name__

        return result

    def _summarize_spec(self, spec: object) -> Dict[str, Any]:
        """Extract friendly summary from an internal spec dataclass object.

        We prefer to include human-readable fields (purpose/description)
        and `config_keys`. For function members, we emit the function
        name rather than the raw callable object.
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
