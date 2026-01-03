"""Extract registry."""

from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.sets.extract.functions import EXTRACT_FUNCTIONS
from fragua.utils.types.enums import ComponentType

EXTRACT_SETS = {
    ComponentType.FUNCTION.value: EXTRACT_FUNCTIONS,
    ComponentType.AGENT.value: FraguaSet("extract_agents", components={}),
}

EXTRACT_REGISTRY = FraguaRegistry("extract_registry", EXTRACT_SETS)
