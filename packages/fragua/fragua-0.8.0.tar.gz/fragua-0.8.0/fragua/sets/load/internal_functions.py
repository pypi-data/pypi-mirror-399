"""
Internal helper functions
"""

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal
from dataclasses import dataclass
import requests
import pandas as pd
from sqlalchemy import create_engine

from fragua.core.set import FraguaSet
from fragua.utils.types.enums import ILF, FieldType

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

# -----------------------
# Load Internal Functions
# -----------------------


def validate_load(
    data: pd.DataFrame,
    directory: str,
) -> None:
    """
    Validate required inputs for load operations.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Load function requires a pandas DataFrame")

    if not directory:
        raise ValueError("'directory' is required")


def validate_sql_load(
    data: pd.DataFrame,
    directory: str,
    table_name: str | None,
) -> None:
    """validate sql required inputs operations."""
    validate_load(data, directory)

    if not table_name:
        raise ValueError("'table_name' is required")


def validate_api_load(
    data: pd.DataFrame,
    url: str,
    method: str,
) -> None:
    """Validate required inputs for API load operations."""
    validate_load(data, url)

    if method not in {"POST", "PUT", "PATCH"}:
        raise ValueError(f"Unsupported HTTP method: {method}")


def build_path(
    file_name: str,
    extension: str = "xlsx",
    directory: str = ".",
) -> dict[str, str]:
    """Build and validate the output file path."""
    return {FieldType.PATH.value: str(Path(directory) / f"{file_name}.{extension}")}


def convert_datetime_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert timezone-aware datetime columns to naive datetime.
    """
    datetime_cols = data.select_dtypes(include=["datetimetz"]).columns
    if len(datetime_cols) > 0:
        data = data.copy()
        for col in datetime_cols:
            data[col] = pd.to_datetime(data[col]).dt.tz_convert(None)

    return data


def write_excel(
    data: pd.DataFrame,
    path: str,
    sheet_name: str | None = None,
    index: bool = False,
    engine: Literal["openpyxl", "xlsxwriter", "odf"] = "openpyxl",
) -> None:
    """
    Write a DataFrame to an Excel file.
    """
    if os.path.exists(path):
        with pd.ExcelWriter(
            path,
            mode="a",
            engine=engine,
            if_sheet_exists="new",
        ) as writer:
            if sheet_name is not None:
                data.to_excel(writer, sheet_name=str(sheet_name), index=index)
            else:
                data.to_excel(writer, index=index)
    else:
        with pd.ExcelWriter(path, engine=engine) as writer:
            if sheet_name is not None:
                data.to_excel(writer, sheet_name=str(sheet_name), index=index)
            else:
                data.to_excel(writer, index=index)


def write_csv(
    data: pd.DataFrame,
    path: str,
    delimiter: str | None,
    encoding: str | None,
    index: bool | None,
) -> None:
    """
    Write a DataFrame to a CSV file.
    """
    data.to_csv(
        path,
        sep=delimiter or ",",
        encoding=encoding or "utf-8",
        index=bool(index),
    )


def write_sql(
    data: pd.DataFrame,
    directory: str,
    table_name: str,
    if_exists: Literal["fail", "replace", "append", "delete_rows"] = "fail",
    index: bool = False,
    chunksize: int | None = None,
) -> pd.DataFrame:
    """Write a DataFrame as an new table into an database."""
    engine = create_engine(directory)

    try:
        data.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=index,
            chunksize=chunksize,
        )
    finally:
        engine.dispose()

    return data


def write_api(
    data: pd.DataFrame,
    url: str,
    method: str,
    headers: dict[str, Any] | None = None,
    timeout: int = 30,
    raise_for_status: bool = True,
) -> pd.DataFrame:
    """Send a DataFrame to an external API endpoint."""

    payload = data.to_dict(orient="records")

    response = requests.request(
        method=method,
        url=url,
        json=payload,
        headers=headers,
        timeout=timeout,
    )

    if raise_for_status:
        response.raise_for_status()

    return data


@dataclass(frozen=True)
class LoadInternalSpec:
    """Specification for internal load helper functions."""

    func: Callable[..., Any]
    description: str
    config_keys: List[str]
    data_arg: str | None = None


INTERNAL_FUNCTIONS: Dict[str, LoadInternalSpec] = {
    ILF.VALIDATE_LOAD.value: LoadInternalSpec(
        func=validate_load,
        description="Validate load inputs.",
        config_keys=[FieldType.DIRECTORY.value],
        data_arg=FieldType.DATA.value,
    ),
    ILF.BUILD_PATH.value: LoadInternalSpec(
        func=build_path,
        description="Build and validate output path.",
        config_keys=[FieldType.DIRECTORY.value, FieldType.FILE_NAME.value],
        data_arg=None,
    ),
    ILF.CONVERT_DATETIME_COLUMNS.value: LoadInternalSpec(
        func=convert_datetime_columns,
        description="Convert timezone-aware datetime columns.",
        config_keys=[],
        data_arg=FieldType.DATA.value,
    ),
    ILF.WRITE_EXCEL.value: LoadInternalSpec(
        func=write_excel,
        description="Write DataFrame to an Excel file.",
        config_keys=[
            FieldType.SHEET_NAME.value,
            FieldType.INDEX.value,
            FieldType.ENGINE.value,
            FieldType.PATH.value,
        ],
        data_arg=FieldType.DATA.value,
    ),
    ILF.WRITE_CSV.value: LoadInternalSpec(
        func=write_csv,
        description="Persist DataFrame to CSV file.",
        config_keys=[
            FieldType.DELIMITER.value,
            FieldType.ENCODING.value,
            FieldType.INDEX.value,
            FieldType.PATH.value,
        ],
        data_arg=FieldType.DATA.value,
    ),
    ILF.VALIDATE_SQL_LOAD.value: LoadInternalSpec(
        func=validate_sql_load,
        description="Validate SQL load configuration.",
        config_keys=[FieldType.DIRECTORY.value, FieldType.TABLE_NAME.value],
        data_arg=FieldType.DATA.value,
    ),
    ILF.WRITE_SQL.value: LoadInternalSpec(
        func=write_sql,
        description="Persist DataFrame into a SQL table.",
        config_keys=[
            FieldType.DIRECTORY.value,
            FieldType.TABLE_NAME.value,
            FieldType.IF_EXISTS.value,
            FieldType.INDEX.value,
            FieldType.CHUNKSIZE.value,
        ],
        data_arg=FieldType.DATA.value,
    ),
    ILF.VALIDATE_API_LOAD.value: LoadInternalSpec(
        func=validate_api_load,
        description="Validate API load configuration.",
        config_keys=[FieldType.URL.value, FieldType.METHOD.value],
        data_arg=FieldType.DATA.value,
    ),
    ILF.WRITE_API.value: LoadInternalSpec(
        func=write_api,
        description="Send DataFrame to an external API endpoint.",
        config_keys=[
            FieldType.URL.value,
            FieldType.METHOD.value,
            FieldType.HEADERS.value,
            FieldType.TIMEOUT.value,
            "raise_for_status",
        ],
        data_arg=FieldType.DATA.value,
    ),
}

# ---------------------------
# Load Internal Functions Set
# ---------------------------
LOAD_INTERNAL_FUNCTIONS = FraguaSet(
    set_name="load_internal_functions", components=INTERNAL_FUNCTIONS
)
