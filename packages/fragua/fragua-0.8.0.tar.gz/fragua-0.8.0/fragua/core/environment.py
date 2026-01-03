"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Literal, overload, cast, Optional

# Placeholder factories for internal functions (avoid name collisions)
from typing import Callable as _Callable
import pandas as _pd

# Import internal spec classes at module level to avoid runtime imports inside methods
from fragua.sets.transform.internal_functions import TransformInternalSpec
from fragua.sets.load.internal_functions import LoadInternalSpec

from fragua.core.agent import FraguaAgent
from fragua.core.sections import FraguaSections
from fragua.core.component import FraguaComponent
from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.core.warehouse import FraguaWarehouse

from fragua.utils.logger import get_logger
from fragua.utils.security.security_context import FraguaSecurityContext, FraguaToken
from fragua.utils.types.enums import ActionType, ComponentType, FieldType


def _make_transform_placeholder(name: str) -> _Callable[..., _pd.DataFrame]:
    def _placeholder(
        df: _pd.DataFrame, *, config: Optional[Dict[str, Any]] = None
    ) -> _pd.DataFrame:  # pragma: no cover - trivial
        raise NotImplementedError(
            f"Internal transform function '{name}' not implemented"
        )

    _placeholder.__name__ = f"__transform_placeholder_{name}"
    return _placeholder


def _make_load_placeholder(name: str) -> _Callable[..., object]:
    def _placeholder(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - trivial
        raise NotImplementedError(f"Internal load function '{name}' not implemented")

    _placeholder.__name__ = f"__load_placeholder_{name}"
    return _placeholder


logger = get_logger(__name__)


class FraguaEnvironment(FraguaComponent):
    """
    Core environment abstraction for Fragua.

    This class represents the top-level orchestration layer of the framework.
    It encapsulates and coordinates all fundamental components, including
    the warehouse, warehouse, action registries, and agents.

    The Environment is responsible for initializing, exposing, and managing
    the lifecycle of all ETL-related components within a given execution context.
    """

    def __init__(self, env_name: str, fg_config: bool = False):
        """
        Initialize a Fragua execution environment.

        This constructor bootstraps all core components required for
        ETL operations, including the warehouse and
        the action registries (extract, transform, load).

        Args:
            env_name (str):
                Logical name of the environment instance.
            fg_config (bool):
                Enables the default Fragua configuration.
                When True, built-in components such as
                functions and agents are automatically registered.
        """

        super().__init__(instance_name=env_name)
        self.fg_config = fg_config
        self.security = FraguaSecurityContext(env_name)
        self.warehouse = self._initialize_warehouse()
        self.sections = self._initialize_actions()

        logger.debug("Environment '%s' initialized.", self.name)

    # -------------------- Internal helpers -------------------- #
    def _token(self, *, kind: str, name: str) -> FraguaToken:
        return self.security.issue_token(
            component_kind=kind,
            component_name=name,
        )

    # ---------------------- Error Handle ---------------------- #
    def agent_not_found(self) -> ValueError:
        """
        Generate a standardized error for missing agents.

        Returns:
            ValueError:
                Exception indicating that the requested agent
                does not exist within the current environment.
        """

        return ValueError("Agent not found.")

    # ---------------------- Initializers ---------------------- #
    def _initialize_warehouse(self) -> FraguaWarehouse:
        """
        Initialize the warehouse for the environment.

        The warehouse serves as the central data container where
        intermediate and final datasets are stored during
        extract, transform, and load operations.

        Returns:
            FraguaWarehouse:
                Initialized warehouse instance bound to this environment.
        """

        warehouse = FraguaWarehouse(f"{self.name}_warehouse", self)

        logger.info("Default warehouse initialized for environment '%s'.", self.name)
        return warehouse

    def _initialize_actions(self) -> FraguaSections:
        """
        Initialize action registries for the environment.

        This method sets up all action-specific registries
        (extract, transform, load), optionally preloading
        default Fragua components when fg_config is enabled.

        Returns:
            FraguaSections:
                Container holding all action registries.
        """

        sections = FraguaSections(self.fg_config)
        logger.info("Default actions initialized for environment '%s'.", self.name)
        return sections

    # ------------------- Helper Properties -------------------- #
    @property
    def extract(self) -> FraguaRegistry:
        """
        Access the Extract action registry.

        Returns:
            ExtractRegistry:
                Registry containing all extract-related components
                (agents, functions, etc).
        """
        return self.sections.extract

    @property
    def transform(self) -> FraguaRegistry:
        """
        Access the Transform action registry.

        Returns:
            TransformRegistry:
                Registry containing all transform-related components
                (agents, functions, etc).
        """
        return self.sections.transform

    @property
    def load(self) -> FraguaRegistry:
        """
        Access the Load action registry.

        Returns:
            LoadRegistry:
                Registry containing all load-related components
                (agents, functions, etc).
        """
        return self.sections.load

    @property
    def functions(self) -> Dict[str, FraguaSet[Any]]:
        """Retrieve all function sets grouped by action."""
        try:
            return self._group_components(ComponentType.FUNCTION)
        except ValueError as exc:
            raise KeyError("Functions set not found in registry.") from exc

    @property
    def agents(self) -> Dict[str, FraguaSet[Any]]:
        """Retrieve all agent sets grouped by action."""
        try:
            return self._group_components(ComponentType.AGENT)
        except ValueError as exc:
            raise KeyError("Agents set not found in registry.") from exc

    # ---------------------- Global API ---------------------- #
    def _get_set(self, action: ActionType, kind: ComponentType) -> FraguaSet[Any]:
        """
        Resolve a FraguaSet by action and component kind.

        If the requested set does not exist and the request concerns
        internal functions, attempt to inject the canonical FraguaSet that
        ships with the corresponding module (e.g. `TRANSFORM_INTERNAL_FUNCTIONS`).
        This enables the environment CRUD API to work even when registries
        were created without the `fg_config` bootstrap.
        """
        registry = self.sections.get_section(action.value)

        fragua_set = registry.get_set(kind.value)

        # If missing, handle special-case for internal functions
        if fragua_set is None and kind is ComponentType.INTERNAL_FUNCTION:
            # Try to attach the canonical internal functions set depending on action
            if action is ActionType.TRANSFORM:
                from fragua.sets.transform.internal_functions import (
                    TRANSFORM_INTERNAL_FUNCTIONS,
                )

                # Register under the expected key so registry.get_set(kind.value)
                # will succeed in subsequent lookups.
                registry.get_sets()[
                    ComponentType.INTERNAL_FUNCTION.value
                ] = TRANSFORM_INTERNAL_FUNCTIONS
                fragua_set = TRANSFORM_INTERNAL_FUNCTIONS

            elif action is ActionType.LOAD:
                from fragua.sets.load.internal_functions import (
                    LOAD_INTERNAL_FUNCTIONS,
                )

                registry.get_sets()[
                    ComponentType.INTERNAL_FUNCTION.value
                ] = LOAD_INTERNAL_FUNCTIONS
                fragua_set = LOAD_INTERNAL_FUNCTIONS

        if fragua_set is None:
            raise ValueError(f"Invalid action type: {action.value}")

        return fragua_set

    def _group_components(self, kind: ComponentType) -> Dict[str, FraguaSet[Any]]:
        """Return a mapping of action name to the corresponding FraguaSet for a kind.

        This consolidates the repeated logic used to build dictionaries of agents
        or functions grouped by action and ensures a single failure mode if a
        set is missing.
        """
        result: Dict[str, FraguaSet[Any]] = {}

        for action in (ActionType.EXTRACT, ActionType.TRANSFORM, ActionType.LOAD):
            result[action.value] = self._get_set(action, kind)

        return result

    def _infer_name_from_component(self, component: Any) -> str:
        """Attempt to infer a registration name from a component.

        - If the component exposes a ``name`` attribute (e.g. FraguaAgent), use it.
        - If the component is a dictionary defining a function record (contains
          the ``FieldType.FUNCTION`` key), use the underlying function's ``__name__``.
        - If the component is callable, use ``component.__name__``.
        - Otherwise raise ValueError requiring an explicit name.
        """
        # FraguaComponent instances expose a .name attribute
        if hasattr(component, "name"):
            name = getattr(component, "name")
            if isinstance(name, str) and name:
                return name

        # If it's a dict-based function record, prefer the callable's __name__ then a dict 'name'
        if isinstance(component, dict):
            func = component.get(FieldType.FUNCTION.value) or component.get("function")
            if callable(func):
                inferred = getattr(func, "__name__", None)
                if isinstance(inferred, str) and inferred:
                    return inferred

            dict_name = component.get("name") or component.get(FieldType.FUNC_KEY.value)
            if isinstance(dict_name, str) and dict_name:
                return dict_name

        # TransformInternalSpec instances: derive name from the underlying callable
        if isinstance(component, TransformInternalSpec):
            inferred = getattr(component.func, "__name__", None)
            if isinstance(inferred, str) and inferred:
                return inferred

        # Callables (functions) typically have __name__
        if callable(component):
            inferred = getattr(component, "__name__", None)
            if isinstance(inferred, str) and inferred:
                return inferred

        raise ValueError(
            "Could not infer a name from component; please provide an explicit 'name' argument."
        )

    def _wrap_internal_function(self, action: ActionType, component: Any) -> Any:
        """Wrap a callable or dict into the appropriate InternalSpec for the action.

        Returns the spec instance or raises ValueError on invalid input.
        """

        if action is ActionType.TRANSFORM:
            # TransformInternalSpec imported at module level

            if callable(component):
                fn = cast(_Callable[..., _pd.DataFrame], component)
                return TransformInternalSpec(func=fn, purpose="", config_keys=[])

            if isinstance(component, dict):
                func = component.get(FieldType.FUNCTION.value) or component.get(
                    "function"
                )
                if not callable(func):
                    raise ValueError(
                        "Invalid internal function component: missing callable under 'function' key"
                    )
                fn = cast(_Callable[..., _pd.DataFrame], func)
                return TransformInternalSpec(
                    func=fn,
                    purpose=str(
                        component.get(
                            FieldType.PURPOSE.value, component.get("purpose", "")
                        )
                        or ""
                    ),
                    config_keys=component.get("config_keys", []),
                )

            if isinstance(component, TransformInternalSpec):
                return component

            raise ValueError(
                "Unsupported type for internal transform function registration"
            )

        if action is ActionType.LOAD:
            # LoadInternalSpec imported at module level

            if callable(component):
                fn = cast(_Callable[..., object], component)
                return LoadInternalSpec(
                    func=fn, description="", config_keys=[], data_arg=None
                )

            if isinstance(component, dict):
                func = component.get(FieldType.FUNCTION.value) or component.get(
                    "function"
                )
                if not callable(func):
                    raise ValueError(
                        "Invalid internal load component: missing callable under 'function' key"
                    )
                fn = cast(_Callable[..., object], func)
                return LoadInternalSpec(
                    func=fn,
                    description=str(
                        component.get(
                            FieldType.PURPOSE.value, component.get("purpose", "")
                        )
                        or ""
                    ),
                    config_keys=component.get("config_keys", []),
                    data_arg=component.get("data_arg"),
                )
            if isinstance(component, LoadInternalSpec):
                return component

            raise ValueError("Unsupported type for internal load function registration")

        raise ValueError(
            "Internal functions can only be created for transform or load actions"
        )

    def _attach_token_if_applicable(self, component: Any, token: FraguaToken) -> None:
        """Attempt to attach a token to component unless it is a frozen spec."""
        # TransformInternalSpec and LoadInternalSpec are imported at module level

        try:
            if hasattr(component, "__dict__") and not isinstance(
                component, (TransformInternalSpec, LoadInternalSpec)
            ):
                component.token = token
        except AttributeError:
            # e.g., dataclasses.FrozenInstanceError when trying to set attr on frozen spec
            pass

    def _prepare_component_for_add(
        self, action: ActionType, kind: ComponentType, component: Any
    ) -> Any:
        """Perform kind-specific normalization of component before adding.

        For internal functions this wraps callables/dicts into the correct Spec type.
        For other kinds, the component is returned as-is.
        """
        if kind is ComponentType.INTERNAL_FUNCTION:
            return self._wrap_internal_function(action, component)
        return component

    @overload
    def get(
        self,
        action: ActionType,
        kind: Literal[ComponentType.AGENT],
        name: str,
    ) -> FraguaAgent: ...

    @overload
    def get(
        self,
        action: ActionType,
        kind: Literal[ComponentType.FUNCTION],
        name: str,
    ) -> Dict[str, Any]: ...

    @overload
    def get(
        self,
        action: ActionType,
        kind: ComponentType,
        name: str,
    ) -> Any: ...

    def get(
        self,
        action: ActionType,
        kind: ComponentType,
        name: str,
    ) -> Any:
        """Retrieve a component by action/kind/name.

        Special-cases `ComponentType.SET` which maps directly to named sets in
        the action registry (i.e. registry.get_set(name)).
        """
        registry = self.sections.get_section(action.value)

        if kind is ComponentType.SET:
            result = registry.get_set(name)
            if result is None:
                raise ValueError("Set not found.")
            return result

        fragua_set = self._get_set(action, kind)
        return fragua_set.get_one(name)

    def add(
        self,
        action: ActionType,
        kind: ComponentType,
        component: Any,
        name: str | None = None,
    ) -> bool:
        """Add component using a small pipeline of handlers.

        Pipeline steps:
            1. Resolve target set
            2. Determine resolved name
            3. Prepare / normalize the component based on kind
            4. Add to set
            5. Attach token when applicable
        """
        # Special-case: adding a new FraguaSet into a registry
        if kind is ComponentType.SET:
            if not isinstance(component, FraguaSet):
                raise ValueError(
                    "To create a new set, provide a FraguaSet instance as component"
                )

            # Register the set into the action's registry
            registry = self.sections.get_section(action.value)
            created = registry.add_set(component)
            if not created:
                return False

            # attach token to the set instance if possible
            token = self._token(kind=kind.value, name=component.set_name)
            self._attach_token_if_applicable(component, token)

            logger.info(
                "%s created: %s (%s)",
                kind.value.capitalize(),
                component.set_name,
                action.value,
            )
            return True

        # 1) Resolve the destination set
        fragua_set = self._get_set(action, kind)

        # 2) Name resolution
        resolved_name = (
            name if name is not None else self._infer_name_from_component(component)
        )

        # 3) Normalize/prepare
        prepared = self._prepare_component_for_add(action, kind, component)

        # 4) Add to the set
        created = fragua_set.add(resolved_name, prepared)
        if not created:
            return False

        # 5) Attach token if appropriate
        token = self._token(kind=kind.value, name=resolved_name)
        self._attach_token_if_applicable(prepared, token)

        logger.info(
            "%s registered: %s (%s)",
            kind.value.capitalize(),
            resolved_name,
            action.value,
        )
        return True

    def update(
        self,
        kind: ComponentType,
        action: ActionType,
        old_name: str,
        new_name: str,
    ) -> bool:
        """Update a component."""
        registry = self.sections.get_section(action.value)

        if kind is ComponentType.SET:
            updated = registry.update_set(old_name, new_name)
            if not updated:
                raise ValueError("Set not found.")
            logger.info(
                "%s renamed: %s -> %s (%s)",
                kind.value.capitalize(),
                old_name,
                new_name,
                action.value,
            )
            return updated

        fragua_set = self._get_set(action, kind)
        updated = fragua_set.update(old_name, new_name)

        if not updated:
            raise ValueError(f"{kind.value.capitalize()} not found.")

        logger.info(
            "%s renamed: %s -> %s (%s)",
            kind.value.capitalize(),
            old_name,
            new_name,
            action.value,
        )

        return updated

    def delete(self, kind: ComponentType, name: str, action: ActionType) -> bool:
        """Delete a component."""
        registry = self.sections.get_section(action.value)

        if kind is ComponentType.SET:
            deleted = registry.delete_set(name)
            if not deleted:
                raise ValueError("Set not found.")
            logger.info(
                "%s deleted: %s (%s)", kind.value.capitalize(), name, action.value
            )
            return deleted

        fragua_set = self._get_set(action, kind)
        deleted = fragua_set.delete_one(name)

        if not deleted:
            raise ValueError(f"{kind.value.capitalize()} not found.")

        logger.info(
            "%s deleted: %s (%s)",
            kind.value.capitalize(),
            name,
            action.value,
        )

        return deleted

    def create(self, action: ActionType, kind: ComponentType, name: str) -> bool:
        """Create and register a new component in the environment.

        Supports creation of standard components (agent, registry, set) and
        also allows creating a placeholder for internal functions under the
        given action (e.g., a transform internal function).
        """

        new_component: Any = None

        # ---------- Component construction ----------
        if kind is ComponentType.AGENT:
            new_component = FraguaAgent(name, self)
            new_component.set_execution_context(action)

        elif kind is ComponentType.REGISTRY:
            new_component = FraguaRegistry(name)

        elif kind is ComponentType.SET:
            new_component = FraguaSet(name)

        elif kind is ComponentType.INTERNAL_FUNCTION:
            # Create a placeholder internal function spec depending on the action
            if action is ActionType.TRANSFORM:
                new_component = TransformInternalSpec(
                    func=_make_transform_placeholder(name),
                    purpose=f"Placeholder: {name}",
                    config_keys=[],
                )

            elif action is ActionType.LOAD:
                new_component = LoadInternalSpec(
                    func=_make_load_placeholder(name),
                    description=f"Placeholder: {name}",
                    config_keys=[],
                    data_arg=None,
                )

            else:
                raise ValueError(
                    "Internal functions can only be created for transform or load actions"
                )

        else:
            raise ValueError(f"Unsupported component type: {kind}")

        # ---------- Registration ----------
        # For internal functions, use fragua_set.add directly to avoid double-wrapping
        if kind is ComponentType.INTERNAL_FUNCTION:
            fragua_set = self._get_set(action, kind)
            created = fragua_set.add(name, new_component)

            if not created:
                return False

            logger.info("Internal_function created: %s (%s)", name, action.value)
            return True

        self.add(action=action, kind=kind, name=name, component=new_component)
        return True

    # ---------------------- Summary ------------------------- #
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the Environment instance.

        This summary aggregates high-level metadata and detailed
        information from all core environment components, including:

        - Environment identity (name and type)
        - Warehouse state and configuration
        - Action registries (extract, transform, load), each including
        their respective agents, functions, etc.

        Returns:
            Dict([str, Any]):
                A hierarchical dictionary representing the complete
                environment configuration and registered components.
        """

        return {
            ComponentType.ENVIRONMENT.value: self.name,
            ComponentType.WAREHOUSE.value: self.warehouse.summary(),
            ComponentType.ACTIONS.value: self.sections.summary(),
        }

    def __repr__(self) -> str:
        return f"<Environment name={self.name!r}>"
