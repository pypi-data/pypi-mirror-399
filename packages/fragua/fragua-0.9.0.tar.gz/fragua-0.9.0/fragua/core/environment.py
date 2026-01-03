"""Base environment class for Fragua, refactored with docstrings.

Provides helpers to register, discover and manage core ETL components
(agents, function registries and the warehouse) within a named environment.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, cast, Optional, overload

# Placeholder factories for internal functions (avoid name collisions)
from typing import Callable as _Callable
import pandas as _pd

# Import internal spec classes at module level to avoid runtime imports inside methods
from fragua.registry.registry import FRAGUA_REGISTRY
from fragua.sets.transform.internal_functions import TransformInternalSpec
from fragua.sets.load.internal_functions import LoadInternalSpec

from fragua.core.agent import FraguaAgent
from fragua.core.component import FraguaComponent
from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.core.warehouse import FraguaWarehouse

from fragua.utils.logger import get_logger
from fragua.utils.security.security_context import FraguaSecurityContext, FraguaToken
from fragua.utils.types.enums import ActionType, ComponentType, FieldType, OperationType


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
    the warehouse, action registries and agents. It is responsible for
    component registration, discovery and lifecycle management.

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
        self.registry = self._initialize_registry()

        logger.debug("Environment '%s' initialized.", self.name)

    # -------------------- Internal helpers -------------------- #
    def _token(self, *, kind: str, name: str) -> FraguaToken:
        return self.security.issue_token(
            component_kind=kind,
            component_name=name,
        )

    def _check_operation_result(self, op: OperationType, result: bool) -> None:
        if not result:
            raise ValueError(f"Failed to execute {op.value} operation.")

    def _check_component_state(self, component: Any) -> None:
        if component is None:
            raise ValueError("Component not found.")

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

    def _initialize_registry(self) -> FraguaRegistry:
        """Initialize fragua registry."""

        # The registry contains several named FraguaSets. Function sets
        # follow the convention "{action}_functions" (e.g. "extract_functions")
        # while internal function specs are kept in their dedicated sets.
        sets: Dict[str, FraguaSet[Any]] = {
            "agent": FraguaSet("agent", components={}),
            "extract_functions": FraguaSet("extract_functions"),
            "transform_functions": FraguaSet("transform_functions"),
            "load_functions": FraguaSet("load_functions"),
            "internal_transform_functions": FraguaSet("internal_transform_functions"),
            "internal_load_functions": FraguaSet("internal_load_functions"),
        }

        # When fg_config is True, use the pre-populated global FRAGUA_REGISTRY
        # so built-in sets/functions are available. Otherwise create a fresh
        # runtime registry instance with the default (empty) sets.
        registry = (
            FRAGUA_REGISTRY
            if self.fg_config
            else FraguaRegistry("fragua_registry", sets=sets)
        )

        return registry

    # ---------------------- Global API ---------------------- #
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
        self, action: ActionType | None, kind: ComponentType, component: Any
    ) -> Any:
        """Perform kind-specific normalization of component before adding.

        For internal functions this wraps callables/dicts into the correct Spec type.
        For other kinds, the component is returned as-is.
        """
        # Normalize internal function registrations (two distinct kinds exist)
        if kind in (
            ComponentType.INTERNAL_TRANSFORM_FUNCTION,
            ComponentType.INTERNAL_LOAD_FUNCTION,
        ):
            if action is None:
                raise ValueError(
                    "Action is required when registering an internal function."
                )
            return self._wrap_internal_function(action, component)

        return component

    def _get_set(self, kind: ComponentType) -> FraguaSet[Any]:

        # Query the registry for a set by its canonical name.
        components_set = self.registry.get_set(kind.value)

        # If the runtime registry does not contain the requested set this
        # is considered a configuration error and we raise to signal it.
        if components_set is None:
            raise ValueError(f"{kind.value.capitalize()} set not found.")

        return components_set

    # get() supports two forms:
    # - get(kind, name)
    # - get(action, ComponentType.FUNCTION, name)
    # Returns None when the requested component or set does not exist.
    @overload
    def get(
        self,
        kind_or_action: Literal[ComponentType.AGENT],
        name_or_kind: str,
        name: None = None,
    ) -> FraguaAgent: ...

    @overload
    def get(
        self,
        kind_or_action: Any,
        name_or_kind: Any | None = None,
        name: str | None = None,
    ) -> Any: ...

    def get(
        self,
        kind_or_action: Any,
        name_or_kind: Any | None = None,
        name: str | None = None,
    ) -> Any:
        """Retrieve a component.

        Usage:
        - get(kind, name)
        - get(action, ComponentType.FUNCTION, name)

        Returns None if the component or set is not found.
        """
        # Action-scoped lookup: get(action, ComponentType.FUNCTION, name)
        # This resolves functions that are registered under a specific action
        # set (e.g. 'extract_functions'). If the named set does not exist we
        # return None to signal an absence rather than raising an exception.
        if isinstance(kind_or_action, ActionType):
            action = kind_or_action
            kind = name_or_kind
            if kind is not ComponentType.FUNCTION:
                raise ValueError(
                    "Action-scoped get is only valid for function components"
                )
            if name is None:
                raise TypeError("Missing component name for action-scoped get()")
            set_name = f"{action.value}_functions"
            components_set = self.registry.get_set(set_name)
            if components_set is None:
                # Set missing: return None (caller may try other actions)
                return None
            return components_set.get_one(name)

        # Standard form: get(kind, name)
        kind = kind_or_action
        if name_or_kind is None:
            raise TypeError("Missing component name")
        component_name = name_or_kind

        if kind is ComponentType.SET:
            return self.registry.get_set(component_name)

        try:
            components_set = self._get_set(kind)
        except ValueError:
            return None

        return components_set.get_one(component_name)

    def add(
        self,
        kind: ComponentType,
        component: Any,
        name: str | None = None,
        action: ActionType | None = None,
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
                    "To create a new set, provide a FraguaSet instance as component."
                )

            # Register the set into the action's registry
            created = self.registry.add_set(component)
            self._check_operation_result(OperationType.CREATE, created)

            # attach token to the set instance if possible
            token = self._token(kind=kind.value, name=component.set_name)
            self._attach_token_if_applicable(component, token)

            logger.info(
                "%s created: %s",
                kind.value.capitalize(),
                component.set_name,
            )
            return True

        # 1) Resolve the destination set
        # Functions are stored in action-specific sets ("{action}_functions").
        if kind is ComponentType.FUNCTION:
            if action is None:
                raise ValueError("Action is required when registering a function.")
            set_name = f"{action.value}_functions"
            component_set = self.registry.get_set(set_name)
            if component_set is None:
                # Missing set indicates a registry misconfiguration
                raise ValueError(f"{set_name} set not found.")
        else:
            component_set = self._get_set(kind)

        # 2) Name resolution
        resolved_name = (
            name if name is not None else self._infer_name_from_component(component)
        )

        # 3) Normalize/prepare
        prepared = self._prepare_component_for_add(action, kind, component)

        # 4) Add to the set
        created = component_set.add(resolved_name, prepared)
        self._check_operation_result(OperationType.CREATE, created)

        # 5) Attach token if appropriate
        token = self._token(kind=kind.value, name=resolved_name)
        self._attach_token_if_applicable(prepared, token)

        logger.info(
            "%s registered: %s (%s)",
            kind.value.capitalize(),
            resolved_name,
            action.value if action is not None else kind.value,
        )
        return True

    def update(
        self,
        kind: ComponentType,
        old_name: str,
        new_name: str,
    ) -> bool:
        """Update a component."""
        components_set = self._get_set(kind)

        updated = components_set.update_one(old_name, new_name)

        self._check_operation_result(OperationType.UPDATE, updated)

        logger.info(
            "%s renamed: %s -> %s",
            kind.value.capitalize(),
            old_name,
            new_name,
        )
        return updated

    def delete(self, kind: ComponentType, name: str) -> bool:
        """Delete a component."""

        components_set = self._get_set(kind)

        deleted = components_set.delete_one(name)

        self._check_operation_result(OperationType.DELETE, deleted)

        logger.info(
            "%s deleted: %s",
            kind.value.capitalize(),
            name,
        )
        return deleted

    def create(
        self, kind: ComponentType, name: str, action: ActionType | None = None
    ) -> bool:
        """Create and register a new component in the environment.

        The `action` parameter is optional to allow creating *unbound* agents
        (i.e., agents that are not yet associated with a specific
        ActionType). When creating internal functions, `action` is required
        and will raise a ValueError if omitted.
        """

        new_component: Any = None

        # ---------- Component construction ----------
        if kind is ComponentType.AGENT:
            new_component = FraguaAgent(name, self)
            # Only set the execution context when an action is provided. This
            # allows creating agents that are not yet bound to an action.
            if action is not None:
                new_component.set_execution_context(action)

        elif kind is ComponentType.REGISTRY:
            new_component = FraguaRegistry(name)

        elif kind is ComponentType.SET:
            new_component = FraguaSet(name)

        # Create a placeholder internal function spec depending on the action
        # These are convenience placeholders for internal transform/load
        # implementations and make it easier to create named internal specs.
        elif kind is ComponentType.INTERNAL_TRANSFORM_FUNCTION:
            new_component = TransformInternalSpec(
                func=_make_transform_placeholder(name),
                purpose=f"Placeholder: {name}",
                config_keys=[],
            )

        elif kind is ComponentType.INTERNAL_LOAD_FUNCTION:
            new_component = LoadInternalSpec(
                func=_make_load_placeholder(name),
                description=f"Placeholder: {name}",
                config_keys=[],
                data_arg=None,
            )

        else:
            raise ValueError(f"Unsupported component type: {kind}")

        # ---------- Registration ----------
        # For internal functions, use fragua_set.add directly to avoid double-wrapping
        if kind in (
            ComponentType.INTERNAL_LOAD_FUNCTION,
            ComponentType.INTERNAL_TRANSFORM_FUNCTION,
        ):
            component_set = self._get_set(kind)

            created = component_set.add(name, new_component)

            self._check_operation_result(OperationType.CREATE, created)

            logger.info(
                "Internal_function created: %s",
                name,
            )
            return True

        # Special-case: if creating an agent without an action, create the
        # instance, register it into the general `agent` set and attach a token.
        if kind is ComponentType.AGENT and action is None:
            token = self._token(kind=kind.value, name=name)

            # Ensure the agent is discoverable by registering it in the agent set
            agent_set = self._get_set(ComponentType.AGENT)
            created = agent_set.add(name, new_component)
            self._check_operation_result(OperationType.CREATE, created)

            # Default the execution context to EXTRACT so convenience methods work
            new_component.set_execution_context(ActionType.EXTRACT)

            # Attach token and finish
            self._attach_token_if_applicable(new_component, token)
            logger.info("Agent created (unbound -> default extract): %s", name)
            return True

        # Otherwise delegate to add() which expects a valid action
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
            ComponentType.REGISTRY.value: self.registry.summary(),
        }

    def __repr__(self) -> str:
        return f"<Environment name={self.name!r}>"
