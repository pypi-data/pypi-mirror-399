"""Fragua Registries Module."""

# Export the singleton registry only. Sub-module discovery/imports were
# removed because those modules are not present in this package layout.
from .registry import FRAGUA_REGISTRY

__all__ = ["FRAGUA_REGISTRY"]
