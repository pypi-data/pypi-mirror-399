"""Actions class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from fragua.core.component import FraguaComponent
from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.registries.extract.registry import EXTRACT_REGISTRY
from fragua.registries.load.registry import LOAD_REGISTRY
from fragua.registries.transform.registry import TRANSFORM_REGISTRY
from fragua.utils.types.enums import ActionType, ComponentType

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment


class FraguaSections(FraguaComponent):
    """Container for all action sections (extract, transform, load)."""

    def __init__(
        self,
        fg_config: bool = False,
    ) -> None:
        super().__init__(instance_name=ComponentType.ACTIONS.value)
        self._extract = (
            EXTRACT_REGISTRY
            if fg_config
            else self._to_empty_registry(FraguaRegistry(ActionType.EXTRACT.value))
        )
        self._transform = (
            TRANSFORM_REGISTRY
            if fg_config
            else self._to_empty_registry(FraguaRegistry(ActionType.TRANSFORM.value))
        )
        self._load = (
            LOAD_REGISTRY
            if fg_config
            else self._to_empty_registry(FraguaRegistry(ActionType.LOAD.value))
        )

    def _to_empty_registry(self, registry: FraguaRegistry) -> FraguaRegistry:
        """
        Populate registries with empty Fragua sets.
        """
        agents_set: FraguaSet[Any] = FraguaSet(ComponentType.AGENT, components={})
        functions_set: FraguaSet[Any] = FraguaSet(ComponentType.FUNCTION, components={})

        registry.add_set(agents_set)
        registry.add_set(functions_set)

        return registry

    def get_section(self, section_name: str) -> FraguaRegistry:
        """Retrive section"""
        section: FraguaRegistry | None = None

        if section_name == ActionType.EXTRACT.value:
            section = self.extract

        if section_name == ActionType.TRANSFORM.value:
            section = self.transform

        if section_name == ActionType.LOAD.value:
            section = self.load

        if section is None:
            raise TypeError(f"{section_name.capitalize()} section not found.")

        return section

    @property
    def extract(self) -> FraguaRegistry:
        """
        Access the Extract action registry.

        Returns:
            The ExtractRegistry instance.
        """
        return self._extract

    @property
    def transform(self) -> FraguaRegistry:
        """
        Access the Transform action registry.

        Returns:
            The TransformRegistry instance.
        """
        return self._transform

    @property
    def load(self) -> FraguaRegistry:
        """
        Access the Load action registry.

        Returns:
            The LoadRegistry instance.
        """
        return self._load

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of all registered actions.

        This method aggregates the summaries of each action registry
        (extract, transform, and load) into a single structured object.


        Returns:
            Dict([str, Any]):
                A dictionary with the following structure:
                - extract (dict): Summary of the Extract registry
                - transform (dict): Summary of the Transform registry
                - load (dict): Summary of the Load registry
        """
        return {
            ActionType.EXTRACT.value: self.extract.summary(),
            ActionType.TRANSFORM.value: self.transform.summary(),
            ActionType.LOAD.value: self.load.summary(),
        }
