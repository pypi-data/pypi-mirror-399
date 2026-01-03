"""
Base classes module.

This module contains:
- Component class.
- Environment class.
- Warehouse class.
- Storage class.
- Set class.
- Registry class.
- Sections class.
"""

from .environment import FraguaEnvironment

from .registry import FraguaRegistry

from .set import FraguaSet

from .sections import FraguaSections

from .agent import FraguaAgent

from .warehouse import FraguaWarehouse

from .storage import Storage, Box, STORAGE_CLASSES

from .component import FraguaComponent

__all__ = [
    # Sections Class
    "FraguaSections",
    # Environment Class
    "FraguaEnvironment",
    # Registry Class
    "FraguaRegistry",
    # Section Fragua Class
    "FraguaSet",
    # Base Fragua Component
    "FraguaComponent",
    # Agent Class
    "FraguaAgent",
    # Warehouse
    "FraguaWarehouse",
    # Storage
    "Storage",
    # Storage Types
    "STORAGE_CLASSES",
    "Box",
]
