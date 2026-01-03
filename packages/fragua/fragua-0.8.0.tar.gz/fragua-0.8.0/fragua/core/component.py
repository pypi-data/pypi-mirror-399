"""Runtime component base."""

from abc import ABC, abstractmethod
from typing import Any, Dict


# pylint: disable=too-few-public-methods


class FraguaComponent(ABC):
    """
    Base class for all components in Fragua.

    FraguaComponent represents stateful objects created during
    environment execution (agents, registries, sets, warehouse, etc.).
    """

    def __init__(self, instance_name: str) -> None:
        self.name = instance_name

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary describing the runtime state
        of the component.
        """
