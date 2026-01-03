"""Fragua agent implementation.

Provides the :class:`FraguaAgent` class which orchestrates extract-transform-load
(ETL) operations inside a :class:`FraguaEnvironment`. Responsibilities include
executing registered functions, creating and storing appropriate Storage
objects (Box or Container), generating and attaching operation metadata,
recording operations with undo support, and interacting with the environment
warehouse.
"""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING
from datetime import datetime, timezone

import pandas as pd

from fragua.core.component import FraguaComponent
from fragua.core.storage import Box, Storage, STORAGE_CLASSES

from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata
from fragua.utils.security.security_context import FraguaToken
from fragua.utils.types.enums import (
    ActionType,
    AttrType,
    ComponentType,
    FieldType,
    MetadataType,
    OperationType,
    StorageType,
    TargetType,
)


if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment

logger = get_logger(__name__)

# pylint: disable=too-many-arguments


class FraguaAgent(FraguaComponent):
    """
    Base class for ETL agents operating within a Fragua Environment.
    """

    _ACTION_STORAGE_MAP: dict[ActionType, StorageType] = {
        ActionType.EXTRACT: StorageType.BOX,
        ActionType.TRANSFORM: StorageType.BOX,
        ActionType.LOAD: StorageType.BOX,
    }

    def __init__(self, agent_name: str, environment: FraguaEnvironment) -> None:
        """Initialize agent with a name and environment."""
        super().__init__(instance_name=agent_name)

        self.environment: FraguaEnvironment = environment
        self.token: FraguaToken
        self.action: ActionType
        self.storage_type: StorageType

        self._operations: List[Dict[str, Any]] = []
        self._undo_stack: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Execution context
    # ------------------------------------------------------------------
    def set_execution_context(self, action: ActionType) -> None:
        """Set the current execution action and corresponding storage type."""
        self.action = action
        self.storage_type = self._ACTION_STORAGE_MAP[action]

    def _require_token(self) -> FraguaToken:
        if self.token is None:
            raise RuntimeError(
                f"Security token not initialized for agent '{self.name}'."
            )
        return self.token

    # ------------------------------------------------------------------
    # Function resolution
    # ------------------------------------------------------------------
    def _get_function(self, function_key: str) -> Any:
        func_spec = self.environment.get(
            self.action,
            ComponentType.FUNCTION,
            function_key,
        )

        if func_spec is None:
            raise ValueError(
                f"Function '{function_key}' not registered for action '{self.action}'."
            )

        func = func_spec[ComponentType.FUNCTION.value]
        func_name = getattr(func, "__name__", function_key)
        return func, func_name

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------
    def _normalize_input_data(self, input_data: Any) -> pd.DataFrame:
        if input_data is None:
            return pd.DataFrame()

        if isinstance(input_data, pd.DataFrame):
            return input_data

        if isinstance(input_data, list):
            return pd.DataFrame(input_data)

        if isinstance(input_data, dict):
            if any(isinstance(v, (list, tuple)) for v in input_data.values()):
                return pd.DataFrame(input_data)
            return pd.DataFrame([input_data])

        raise TypeError(f"Unsupported input_data type: {type(input_data).__name__}")

    def _check_input_data(
        self,
        input_data: pd.DataFrame | None,
        apply_to: str | list[str] | None,
    ) -> pd.DataFrame | None:
        if input_data is None and apply_to is not None:
            if isinstance(apply_to, list):
                return pd.concat(
                    [self.get_from_warehouse(name).data for name in apply_to]
                )
            return self.get_from_warehouse(apply_to).data

        return input_data

    # ------------------------------------------------------------------
    # Storage creation
    # ------------------------------------------------------------------
    def _generate_storage_name(self, function_name: str) -> str:
        return f"{function_name}_{self.action.value}_data"

    def create_storage(
        self,
        *,
        data: Any,
        function_name: str,
        storage_name: str | None = None,
    ) -> Storage[Any]:
        """Create the appropriate Storage (Box) for the given data and function name."""
        storage_cls = STORAGE_CLASSES.get(self.storage_type)

        if not storage_cls:
            raise TypeError(f"Invalid storage type: '{self.storage_type}'.")

        name = storage_name or self._generate_storage_name(function_name)

        return storage_cls(name, data)

    # ------------------------------------------------------------------
    # Warehouse access
    # ------------------------------------------------------------------
    def add_to_warehouse(
        self,
        storage: Storage[Box],
        storage_name: str | None = None,
        *,
        overwrite: bool = False,
    ) -> bool:
        """Add a Storage to the environment warehouse; returns True if added."""
        name = storage_name or getattr(storage, AttrType.NAME.value, None)
        if not name:
            raise ValueError("Storage name could not be resolved.")

        return self.environment.warehouse.add_storage(
            name=name,
            storage=storage,
            token=self._require_token(),
            agent_name=self.name,
            overwrite=overwrite,
        )

    def auto_store(self, storage: Storage[Box]) -> None:
        """Convenience to add storage to the warehouse without explicit name."""
        self.add_to_warehouse(storage)

    def get_from_warehouse(self, storage_name: str) -> Box:
        """Retrieve a Box storage by name from the environment warehouse."""
        storage = self.environment.warehouse.get_storages(
            token=self.token,
            storage_name=storage_name,
            agent_name=self.name,
        )

        if storage is None:
            raise TypeError("Storage not found in warehouse.")
        if not isinstance(storage, Box):
            raise TypeError("Storage is not a Box.")

        return storage

    # ------------------------------------------------------------------
    # Containers (removed)
    # ------------------------------------------------------------------

    def _resolve_load_kwargs(self, box_name: str, **kwargs: Any) -> dict[str, Any]:
        resolved = dict(kwargs)
        if resolved.get(FieldType.SHEET_NAME.value) is None:
            resolved[FieldType.SHEET_NAME.value] = box_name
        if resolved.get(FieldType.TABLE_NAME.value) is None:
            resolved[FieldType.TABLE_NAME.value] = box_name
        return resolved

    # ------------------------------------------------------------------
    # Metadata & operations
    # ------------------------------------------------------------------
    def _generate_operation_metadata(
        self, target_name: str, storage: Storage[Any]
    ) -> None:
        metadata = generate_metadata(
            storage=storage,
            metadata_type=MetadataType.OPERATION.value,
            target_name=target_name,
        )
        add_metadata_to_storage(storage, metadata)

    def _register_operation(self, func_name: str) -> None:
        self._operations.append(
            {
                FieldType.ACTION.value: self.action.value,
                ComponentType.FUNCTION.value: func_name,
                MetadataType.TIMESTAMP.value: datetime.now(timezone.utc),
            }
        )
        self._undo_stack.append(
            {
                MetadataType.OPERATION.value: "workflow",
                ComponentType.FUNCTION.value: func_name,
            }
        )

    def get_operations(self) -> pd.DataFrame:
        """Return recorded operations as a pandas DataFrame."""
        return pd.DataFrame(self._operations)

    def undo_last_operation(self) -> bool:
        """Undo the last registered operation and return True if successful."""
        if not self._undo_stack:
            return False

        last = self._undo_stack.pop()
        func_name = last.get(ComponentType.FUNCTION.value)

        self._operations = [
            op
            for op in self._operations
            if op.get(ComponentType.FUNCTION.value) != func_name
        ]

        logger.info("Undid last operation: %s", func_name)
        return True

    # ------------------------------------------------------------------
    # Core execution pipeline
    # ------------------------------------------------------------------
    def _execute(
        self,
        *,
        action: ActionType,
        target_type: str | None,
        function_callable: Any | None = None,
        function_name: str | None = None,
        input_data: pd.DataFrame | None = None,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute a resolved function for the given action and target.

        If ``function_callable`` is provided it will be used instead of resolving
        the function via the environment registry. ``function_name`` may be used
        to provide a human-readable name for metadata and storage naming.
        """
        self.set_execution_context(action)

        # Resolve function and name
        if function_callable is None:
            if not target_type:
                raise TypeError(
                    "Missing 'target_type' when resolving function from registry"
                )
            func, func_name = self._get_function(target_type)
        else:
            func = function_callable
            func_name = function_name or getattr(
                function_callable, "__name__", target_type or "<unknown>"
            )

        data = self._normalize_input_data(input_data)

        if action is ActionType.EXTRACT:
            result = func(**kwargs)
            if not isinstance(result, pd.DataFrame):
                raise TypeError("EXTRACT functions must return a DataFrame")
        else:
            # Some user-provided transform functions expect a positional first
            # argument (often named 'data') while others expect the keyword
            # 'input_data'. Try keyword first and fall back to positional.
            try:
                result = func(input_data=data, **kwargs)
            except TypeError as exc:  # try fallback to positional
                msg = str(exc)
                if "input_data" in msg or "unexpected keyword" in msg:
                    result = func(data, **kwargs)
                else:
                    raise

            if action is ActionType.TRANSFORM and not isinstance(result, pd.DataFrame):
                raise TypeError("TRANSFORM functions must return a DataFrame")

        storage = self.create_storage(
            data=result,
            function_name=func_name,
            storage_name=save_as,
        )

        # Use the function name for operation metadata and registration
        self._generate_operation_metadata(func_name, storage)
        self._register_operation(func_name)
        self.auto_store(storage)

    # ------------------------------------------------------------------
    # Public work API
    # ------------------------------------------------------------------
    def work(
        self,
        *,
        target_type: str | None = None,
        function: Any | None = None,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        input_data: pd.DataFrame | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Execute a work unit for the given target type and return the agent for chaining.

        Parameters
        - ``target_type``: key identifying the target/function to execute (e.g. 'csv', 'report').
          If omitted, ``function`` must be provided.
        - ``function``: optional callable or name (str) to override which function to run. If a
          string is provided it will be looked up in the current action's function set.
        """
        input_data = self._check_input_data(input_data, apply_to)

        logger.debug(
            "work called: target_type=%r function=%r apply_to=%r save_as=%r",
            target_type,
            function,
            apply_to,
            save_as,
        )

        if target_type is None and function is None:
            raise TypeError(
                "Missing required keyword argument 'target_type'",
                " (or provide 'function' as a callable or registered function name).",
            )

        # If no explicit function override, proceed normally
        if function is None:
            self._execute(
                action=self.action,
                target_type=target_type,
                input_data=input_data,
                save_as=save_as,
                **kwargs,
            )
            return self

        # If a string provided, look up the function spec in the environment
        if isinstance(function, str):
            # Build ordered list: prefer current action, then try the others
            actions_to_try = [
                self.action,
                ActionType.EXTRACT,
                ActionType.TRANSFORM,
                ActionType.LOAD,
            ]
            func_spec: Any | None = None
            action_to_use: ActionType | None = None

            for action_candidate in actions_to_try:
                # avoid checking same action twice
                if action_candidate == self.action and action_candidate in (
                    ActionType.EXTRACT,
                    ActionType.TRANSFORM,
                    ActionType.LOAD,
                ):
                    pass

                candidate = self.environment.get(
                    action_candidate, ComponentType.FUNCTION, function
                )
                if candidate is not None:
                    func_spec = candidate
                    action_to_use = action_candidate
                    break

            if func_spec is None:
                raise ValueError(
                    f"Function '{function}' not registered for action '{self.action}'."
                )

            # func_spec can be either a dict record or a callable that was
            # registered directly. Handle both shapes explicitly.
            if isinstance(func_spec, dict):
                func_callable = func_spec[ComponentType.FUNCTION.value]
            elif callable(func_spec):
                func_callable = func_spec
            else:
                raise TypeError("Registered function has unsupported format.")

            func_name = getattr(func_callable, "__name__", function)

            self._execute(
                action=action_to_use or self.action,
                target_type=target_type,
                function_callable=func_callable,
                function_name=func_name,
                input_data=input_data,
                save_as=save_as,
                **kwargs,
            )
            return self

        # If a callable provided, use it directly
        if callable(function):
            func_callable = function
            func_name = getattr(function, "__name__", target_type)

            self._execute(
                action=self.action,
                target_type=target_type,
                function_callable=func_callable,
                function_name=func_name,
                input_data=input_data,
                save_as=save_as,
                **kwargs,
            )
            return self

        raise TypeError(
            "'function' must be either a callable or the name (str) of a registered function"
        )

    # ------------------------------------------------------------------
    # High-level fluent helpers
    # ------------------------------------------------------------------
    def _pipeline(
        self,
        *,
        target_type: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        self.work(
            target_type=target_type,
            apply_to=apply_to,
            save_as=save_as,
            **kwargs,
        )
        return self

    # ---------------- Extract ----------------
    def from_csv(
        self, *, path: str, save_as: str | None = None, **kwargs: Any
    ) -> "FraguaAgent":
        """Extract data from a CSV file and optionally save it in the warehouse."""
        return self._pipeline(
            target_type=TargetType.CSV.value,
            path=path,
            save_as=save_as,
            **kwargs,
        )

    def from_excel(
        self,
        *,
        path: str,
        sheet_name: str | int = 0,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Extract data from an Excel file and optionally save it in the warehouse."""
        return self._pipeline(
            target_type=TargetType.EXCEL.value,
            path=path,
            sheet_name=sheet_name,
            save_as=save_as,
            **kwargs,
        )

    def from_sql(
        self,
        *,
        connection_string: str,
        query: str,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Extract data with a SQL query and optionally save it in the warehouse."""
        return self._pipeline(
            target_type=TargetType.SQL.value,
            connection_string=connection_string,
            query=query,
            save_as=save_as,
            **kwargs,
        )

    def from_api(
        self,
        *,
        url: str,
        method: str = OperationType.GET.value,
        headers: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        data: Dict[str, Any] | None = None,
        auth: Dict[str, str] | None = None,
        proxy: Dict[str, str] | None = None,
        timeout: int | None = None,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Extract data from an API endpoint and optionally save it in the warehouse."""
        return self._pipeline(
            target_type=TargetType.API.value,
            url=url,
            method=method,
            headers=headers,
            params=params,
            data=data,
            auth=auth,
            proxy=proxy,
            timeout=timeout,
            save_as=save_as,
            **kwargs,
        )

    # ---------------- Transform ----------------
    def to_ml(
        self,
        *,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        input_data: pd.DataFrame | None = None,
        config_keys: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Apply ML transform and return agent for chaining."""
        # Ensure execution context is set for transform actions
        self.set_execution_context(ActionType.TRANSFORM)

        input_data = self._check_input_data(input_data, apply_to)

        return self._pipeline(
            target_type=TargetType.ML.value,
            apply_to=apply_to,
            save_as=save_as,
            input_data=input_data,
            config_keys=config_keys,
            **kwargs,
        )

    def to_report(
        self,
        *,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        input_data: pd.DataFrame | None = None,
        config_keys: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Apply report transform and return agent for chaining."""
        self.set_execution_context(ActionType.TRANSFORM)

        input_data = self._check_input_data(input_data, apply_to)

        return self._pipeline(
            target_type=TargetType.REPORT.value,
            apply_to=apply_to,
            save_as=save_as,
            input_data=input_data,
            config_keys=config_keys,
            **kwargs,
        )

    def to_analysis(
        self,
        *,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        input_data: pd.DataFrame | None = None,
        config_keys: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Apply analysis transform and return agent for chaining."""
        self.set_execution_context(ActionType.TRANSFORM)

        input_data = self._check_input_data(input_data, apply_to)

        return self._pipeline(
            target_type=TargetType.ANALYSIS.value,
            apply_to=apply_to,
            save_as=save_as,
            input_data=input_data,
            config_keys=config_keys,
            **kwargs,
        )

    # ---------------- Load ----------------
    def _load(self, target_type: str, apply_to: str | list[str], **kwargs: Any) -> None:
        if not apply_to:
            raise TypeError("Missing required argument: 'apply_to'.")

        names = [apply_to] if isinstance(apply_to, str) else apply_to

        for box_name in names:
            box = self.get_from_warehouse(box_name)
            params = self._resolve_load_kwargs(box_name, **kwargs)

            self._execute(
                action=ActionType.LOAD,
                target_type=target_type,
                input_data=box.data,
                **params,
            )

    def to_csv(
        self,
        *,
        apply_to: str | list[str],
        directory: str | None = None,
        file_name: str | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Load specified warehouse storage(s) to CSV targets and return agent for chaining."""
        self.set_execution_context(ActionType.LOAD)
        self._load(
            TargetType.CSV.value,
            apply_to,
            directory=directory,
            file_name=file_name,
            **kwargs,
        )
        return self

    def to_excel(
        self,
        *,
        apply_to: str | list[str],
        directory: str | None = None,
        file_name: str | None = None,
        sheet_name: str | int | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Load specified warehouse storage(s) to Excel targets and return agent for chaining."""
        self.set_execution_context(ActionType.LOAD)
        self._load(
            TargetType.EXCEL.value,
            apply_to,
            directory=directory,
            file_name=file_name,
            sheet_name=sheet_name,
            **kwargs,
        )
        return self

    def to_sql(
        self,
        *,
        apply_to: str | list[str],
        connection_string: str | None = None,
        table_name: str | None = None,
        if_exists: str | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Load specified warehouse storage(s) to SQL targets and return agent for chaining."""
        self.set_execution_context(ActionType.LOAD)
        self._load(
            TargetType.SQL.value,
            apply_to,
            connection_string=connection_string,
            table_name=table_name,
            if_exists=if_exists,
            **kwargs,
        )
        return self

    def to_api(
        self,
        *,
        apply_to: str | list[str],
        url: str | None = None,
        method: str = OperationType.POST.value,
        headers: Dict[str, Any] | None = None,
        params: Dict[str, Any] | None = None,
        data: Dict[str, Any] | None = None,
        auth: Dict[str, str] | None = None,
        proxy: Dict[str, str] | None = None,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> "FraguaAgent":
        """Load specified warehouse storage(s) to API endpoints and return agent for chaining."""
        self.set_execution_context(ActionType.LOAD)
        self._load(
            TargetType.API.value,
            apply_to,
            url=url,
            method=method,
            headers=headers,
            params=params,
            data=data,
            auth=auth,
            proxy=proxy,
            timeout=timeout,
            **kwargs,
        )
        return self

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    def summary(self) -> Dict[str, Any]:
        """Return agent metadata and a serialized view of recent operations."""
        env_name = getattr(self.environment, AttrType.NAME.value, None)

        ops_serialized = []

        for op in self._operations:
            ts = op.get(MetadataType.TIMESTAMP.value)

            ops_serialized.append(
                {
                    FieldType.ACTION.value: op.get(FieldType.ACTION.value),
                    ComponentType.FUNCTION.value: op.get(ComponentType.FUNCTION.value),
                    MetadataType.TIMESTAMP.value: (
                        ts.isoformat() if ts is not None else None
                    ),
                }
            )

        undo_serialized = [
            {
                MetadataType.OPERATION.value: item.get(MetadataType.OPERATION.value),
                ComponentType.FUNCTION.value: item.get(ComponentType.FUNCTION.value),
            }
            for item in self._undo_stack
        ]

        return {
            ComponentType.AGENT.value: self.name,
            MetadataType.TOKEN_ID.value: self.token.token_id,
            FieldType.ACTION.value: self.action.value,
            FieldType.STORAGE_TYPE.value: self.storage_type.value,
            ComponentType.ENVIRONMENT.value: env_name,
            MetadataType.OPERATIONS_COUNT.value: len(self._operations),
            MetadataType.OPERATIONS_DONE.value: ops_serialized,
            "undo_stack_size": len(self._undo_stack),
            "undo_stack": undo_serialized,
        }
