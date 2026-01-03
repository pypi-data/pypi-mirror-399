"""Load Functions Set."""

from typing import Any, Callable, Dict, Iterable, List, Union

import pandas as pd

from fragua.core.set import FraguaSet
from fragua.sets.load.internal_functions import INTERNAL_FUNCTIONS

from fragua.utils.types.enums import ILF, ActionType, FieldType, TargetType


# -----------------
# Load Functions
# -----------------


def execute_load_pipeline(
    input_data: pd.DataFrame,
    steps: Iterable[str],
    **kwargs: Any,
) -> pd.DataFrame:
    """Execute a sequence of load internal functions as a pipeline."""
    data = input_data
    context: dict[str, Any] = dict(kwargs)

    for step in steps:
        if step not in INTERNAL_FUNCTIONS:
            raise KeyError(f"Load function '{step}' not registered.")

        spec = INTERNAL_FUNCTIONS[step]

        call_kwargs = {key: context[key] for key in spec.config_keys if key in context}

        if spec.data_arg:
            result = spec.func(**{spec.data_arg: data}, **call_kwargs)
        else:
            result = spec.func(**call_kwargs)

        if isinstance(result, dict):
            context.update(result)
        elif isinstance(result, pd.DataFrame):
            data = result

    return data


def load_excel(
    input_data: pd.DataFrame,
    **kwargs: Any,
) -> pd.DataFrame:
    """Export a DataFrame to an Excel file."""
    return execute_load_pipeline(
        input_data=input_data,
        steps=[
            ILF.VALIDATE_LOAD.value,
            ILF.BUILD_PATH.value,
            ILF.CONVERT_DATETIME_COLUMNS.value,
            ILF.WRITE_EXCEL.value,
        ],
        **kwargs,
    )


def load_csv(
    input_data: pd.DataFrame,
    **kwargs: Any,
) -> pd.DataFrame:
    """Export a DataFrame to a CSV file."""
    return execute_load_pipeline(
        input_data=input_data,
        steps=[
            ILF.VALIDATE_LOAD.value,
            ILF.BUILD_PATH.value,
            ILF.WRITE_CSV.value,
        ],
        **kwargs,
    )


def load_sql(
    input_data: pd.DataFrame,
    **kwargs: Any,
) -> pd.DataFrame:
    """Persist a DataFrame into a SQL database table."""
    return execute_load_pipeline(
        input_data=input_data,
        steps=[
            ILF.VALIDATE_SQL_LOAD.value,
            ILF.WRITE_SQL.value,
        ],
        **kwargs,
    )


def load_api(
    input_data: pd.DataFrame,
    **kwargs: Any,
) -> pd.DataFrame:
    """Send data to an external API."""
    return execute_load_pipeline(
        input_data=input_data,
        steps=[
            ILF.VALIDATE_API_LOAD.value,
            ILF.WRITE_API.value,
        ],
        **kwargs,
    )


FUNCTIONS: Dict[str, Dict[str, Union[str, Callable[..., Any], List[str]]]] = {
    TargetType.EXCEL.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.PURPOSE.value: "Export a DataFrame to an Excel file.",
        FieldType.FUNCTION.value: load_excel,
        FieldType.STEPS.value: [
            ILF.VALIDATE_LOAD.value,
            ILF.BUILD_PATH.value,
            ILF.CONVERT_DATETIME_COLUMNS.value,
            ILF.WRITE_EXCEL.value,
        ],
    },
    TargetType.CSV.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.PURPOSE.value: "Export a DataFrame to a CSV file.",
        FieldType.FUNCTION.value: load_csv,
        FieldType.STEPS.value: [
            ILF.VALIDATE_LOAD.value,
            ILF.BUILD_PATH.value,
            ILF.WRITE_CSV.value,
        ],
    },
    TargetType.SQL.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.PURPOSE.value: "Persist a DataFrame into a SQL database table.",
        FieldType.FUNCTION.value: load_sql,
        FieldType.STEPS.value: [
            ILF.VALIDATE_SQL_LOAD.value,
            ILF.WRITE_SQL.value,
        ],
    },
    TargetType.API.value: {
        FieldType.ACTION.value: ActionType.LOAD.value,
        FieldType.PURPOSE.value: "Send data to an external API.",
        FieldType.FUNCTION.value: load_api,
        FieldType.STEPS.value: [
            ILF.VALIDATE_API_LOAD.value,
            ILF.WRITE_API.value,
        ],
    },
}

# ---------------------
# Load Functions Set
# ---------------------

LOAD_FUNCTIONS = FraguaSet(set_name="load_functions", components=FUNCTIONS)
