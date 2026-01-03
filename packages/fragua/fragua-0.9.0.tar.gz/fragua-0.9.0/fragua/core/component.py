"""Core runtime component base classes.

This module provides the abstract base used by all runtime
components that live inside a Fragua environment (agents,
registries, sets, warehouse, etc.). Subclasses implement the
`summary()` API which is used for inspection and for building
human-friendly representations of runtime state.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


# pylint: disable=too-few-public-methods


class FraguaComponent(ABC):
    """
    Abstract base for Fragua runtime components.

    Subclasses represent stateful objects that are created and
    managed by a `FraguaEnvironment`. Implementations must provide
    a `summary()` method which returns a serializable mapping with
    relevant metadata and status information.

    Attributes
    ----------
    name:
        Logical instance name used to reference the component
        within registries and logs.
    """

    def __init__(self, instance_name: str) -> None:
        # Store the canonical name used to register or reference this
        # component within the environment and registry systems.
        self.name = instance_name

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary describing the runtime state
        of the component.

        The returned dictionary should be JSON-serializable and
        contain human-friendly fields (for example: name, type,
        counts, or configuration metadata). Example:

        {
            "name": "my_agent",
            "type": "agent",
            "operations_count": 10,
        }
        """
