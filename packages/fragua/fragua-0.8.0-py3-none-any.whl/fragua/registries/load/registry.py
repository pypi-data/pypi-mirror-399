"""Load registry."""

from typing import Any, Dict
from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.sets.load.functions import LOAD_FUNCTIONS
from fragua.sets.load.internal_functions import LOAD_INTERNAL_FUNCTIONS
from fragua.utils.types.enums import ComponentType

LOAD_SETS: Dict[str, FraguaSet[Any]] = {
    ComponentType.FUNCTION.value: LOAD_FUNCTIONS,
    ComponentType.INTERNAL_FUNCTION.value: LOAD_INTERNAL_FUNCTIONS,
    ComponentType.AGENT.value: FraguaSet("load_agents", components={}),
}

LOAD_REGISTRY = FraguaRegistry("load_registry", LOAD_SETS)
