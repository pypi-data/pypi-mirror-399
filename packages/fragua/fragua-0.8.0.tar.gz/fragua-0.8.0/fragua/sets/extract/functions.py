"""Fragua functions set."""

from pathlib import Path
from typing import Callable, Dict, Any, Mapping, MutableMapping, Union

import pandas as pd
from sqlalchemy import create_engine
import requests
from requests.auth import HTTPBasicAuth

from fragua.core.set import FraguaSet
from fragua.utils.types.enums import ActionType, FieldType, OperationType, TargetType

# pylint: disable=too-many-arguments

# -----------------
# Extract Functions
# -----------------


def extract_csv(*, path: str, **_: Any) -> pd.DataFrame:
    """Extract tabular data from a CSV file."""
    if not path:
        raise ValueError("'path' is required")

    return pd.read_csv(Path(path))


def extract_excel(
    *,
    path: str,
    sheet_name: str | int = 0,
    **_: Any,
) -> pd.DataFrame:
    """Extract data from an Excel spreadsheet."""
    if not path:
        raise ValueError("'path' is required")

    df = pd.read_excel(
        Path(path),
        sheet_name=sheet_name,
    )

    if isinstance(df, dict):
        raise TypeError(
            "extract_excel must return a pandas DataFrame, got multiple sheets"
        )

    return df


def extract_sql(
    *,
    connection_string: str,
    query: str,
    **_: Any,
) -> pd.DataFrame:
    """Execute a SQL query and extract the result as a DataFrame."""
    if not connection_string or not query:
        raise ValueError("'connection_string' and 'query' are required")

    engine = create_engine(connection_string)
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)
    finally:
        engine.dispose()


def extract_api(
    *,
    url: str,
    method: str = OperationType.GET.value,
    headers: Mapping[str, Any] | None = None,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    auth: Mapping[str, str] | None = None,
    proxy: MutableMapping[str, str] | None = None,
    timeout: int | None = None,
    **_: Any,
) -> pd.DataFrame:
    """Fetch JSON data from a REST API endpoint."""
    if not url:
        raise ValueError("'url' is required")

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        data=data,
        auth=HTTPBasicAuth(**auth) if auth else None,
        proxies=proxy,
        timeout=timeout,
    )
    response.raise_for_status()

    payload = response.json()

    if isinstance(payload, list):
        return pd.DataFrame(payload)

    if isinstance(payload, dict):
        return pd.json_normalize(payload)

    raise ValueError(f"Unexpected API response type: {type(payload)}")


FUNCTIONS: Dict[str, Dict[str, Union[str, Callable[..., Any]]]] = {
    TargetType.CSV.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.PURPOSE.value: "Extract tabular data from a CSV file.",
        FieldType.FUNCTION.value: extract_csv,
    },
    TargetType.EXCEL.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.PURPOSE.value: "Extract data from an Excel spreadsheet.",
        FieldType.FUNCTION.value: extract_excel,
    },
    TargetType.SQL.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.PURPOSE.value: "Execute a SQL query and extract the result as a DataFrame.",
        FieldType.FUNCTION.value: extract_sql,
    },
    TargetType.API.value: {
        FieldType.ACTION.value: ActionType.EXTRACT.value,
        FieldType.PURPOSE.value: "Fetch JSON data from a REST API endpoint.",
        FieldType.FUNCTION.value: extract_api,
    },
}

# ---------------------
# Extract Functions Set
# ---------------------

EXTRACT_FUNCTIONS = FraguaSet(set_name="extract_functions", components=FUNCTIONS)
