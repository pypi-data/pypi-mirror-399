"""
This module patches the Databricks SQLAlchemy dialect to facilitate schema
reflection.

This is needed because `databricks-sqlalchemy` uses `DESCRIBE TABLE EXTENDED`,
which does not provide enough information to reflect primary keys and foreign
keys correctly.
"""

import re
from collections.abc import Callable
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

import sqlalchemy
from databricks.sqlalchemy import DatabricksDialect
from sqlalchemy import text, types
from sqlalchemy.engine.base import Connection
from typing_extensions import ParamSpec, TypedDict

from db_diagram._utilities import cache, get_bind_database_schema

if TYPE_CHECKING:
    from databricks.sql.client import (
        Connection as DatabricksConnection,
    )
    from databricks.sql.client import Cursor
    from databricks.sql.types import Row as DatabricksRow
    from sqlalchemy.engine import CursorResult
    from sqlalchemy.engine.row import Row

_GET_COLUMNS_TYPE_MAP: dict[str, type] = {
    "boolean": sqlalchemy.types.Boolean,
    "smallint": sqlalchemy.types.SmallInteger,
    "int": sqlalchemy.types.Integer,
    "bigint": sqlalchemy.types.BigInteger,
    "float": sqlalchemy.types.Float,
    "double": sqlalchemy.types.Float,
    "string": sqlalchemy.types.String,
    "varchar": sqlalchemy.types.String,
    "char": sqlalchemy.types.String,
    "binary": sqlalchemy.types.String,
    "array": sqlalchemy.types.String,
    "map": sqlalchemy.types.String,
    "struct": sqlalchemy.types.String,
    "uniontype": sqlalchemy.types.String,
    "decimal": sqlalchemy.types.Numeric,
    "date": sqlalchemy.types.Date,
    "timestamp": sqlalchemy.types.TIMESTAMP,
}

_CONSTRAINT_SELECT_STATEMENT: str = """
with key_column_usage as (
    select
    constraint_catalog,
    constraint_schema,
    constraint_name,
    table_name,
    column_name,
    ordinal_position,
    position_in_unique_constraint
    from information_schema.key_column_usage
),
all_constraints as (
    select
    key_column_usage.constraint_catalog,
    key_column_usage.constraint_schema,
    key_column_usage.constraint_name,
    table_constraints.constraint_type,
    key_column_usage.table_name,
    key_column_usage.column_name,
    key_column_usage.ordinal_position,
    constraint_table_usage.table_name as referenced_table,
    referenced_key_column_usage.column_name as referenced_column,
    referenced_key_column_usage.constraint_schema as referenced_schema
    from key_column_usage
    left join information_schema.constraint_table_usage
    on key_column_usage.constraint_catalog
      = constraint_table_usage.constraint_catalog
    and key_column_usage.constraint_schema
      = constraint_table_usage.constraint_schema
    and key_column_usage.constraint_name
      = constraint_table_usage.constraint_name
    join information_schema.table_constraints
    on key_column_usage.constraint_catalog
      = table_constraints.constraint_catalog
    and key_column_usage.constraint_schema
      = table_constraints.constraint_schema
    and key_column_usage.constraint_name
      = table_constraints.constraint_name
    left join information_schema.referential_constraints
    on table_constraints.constraint_name
      = referential_constraints.constraint_name
    and table_constraints.constraint_schema
      = referential_constraints.constraint_schema
    and table_constraints.constraint_catalog
      = referential_constraints.constraint_catalog
    left join key_column_usage as referenced_key_column_usage
    on referenced_key_column_usage.constraint_name
      = referential_constraints.unique_constraint_name
    and referenced_key_column_usage.constraint_catalog
      = referential_constraints.constraint_catalog
    and referenced_key_column_usage.constraint_schema
      = referential_constraints.constraint_schema
    and referenced_key_column_usage.ordinal_position
      = key_column_usage.position_in_unique_constraint
)
select * from all_constraints
where constraint_schema = :schema
and constraint_type in ('PRIMARY KEY', 'FOREIGN KEY')
order by ordinal_position asc
"""


class _ReflectedConstraint(TypedDict):
    name: str | None


class _ReflectedPrimaryKeyConstraint(_ReflectedConstraint):
    constrained_columns: list[str]


class _ReflectedForeignKeyConstraint(_ReflectedConstraint):
    constrained_columns: list[str]
    referred_schema: str
    referred_table: str
    referred_columns: list[str]


class _ReflectedColumn(TypedDict):
    name: str
    type: types.TypeEngine[Any]
    nullable: bool
    default: str | None


_DatabricksParamSpec = ParamSpec("_DatabricksParamSpec")


# region Patch Dialect


# Save a reference to unpatched methods
_original_databricks_dialect_get_table_names: Callable[
    _DatabricksParamSpec, list[str]
] = DatabricksDialect.get_table_names  # type: ignore
_original_databricks_dialect_get_view_names: Callable[
    _DatabricksParamSpec, list[str]
] = DatabricksDialect.get_view_names  # type: ignore
_original_databricks_dialect_has_table: Callable[
    _DatabricksParamSpec, bool
] = DatabricksDialect.has_table  # type: ignore


def _databricks_dialect_has_table(
    self: DatabricksDialect,
    connection: Connection,
    table_name: str,
    schema: str | None = None,
    **kwargs: Any,
) -> bool:
    if len(table_name) == 0:
        return False
    return _original_databricks_dialect_has_table(
        self, connection, table_name, schema, **kwargs
    )


@wraps(DatabricksDialect.get_pk_constraint)
def _databricks_dialect_get_pk_constraint(
    self: DatabricksDialect,
    connection: Connection,
    table_name: str,
    schema: str | None = None,
    **kwargs: Any,
) -> _ReflectedPrimaryKeyConstraint | None:
    if not schema:
        schema = get_bind_database_schema(connection).schema
    if not schema:
        raise RuntimeError(repr(locals()))
    primary_key_constraints: tuple[_ReflectedPrimaryKeyConstraint, ...] = (
        tuple(
            _databricks_dialect_get_schema_constraints(connection, schema)
            .get("PRIMARY KEY", {})
            .get(table_name, {})
            .values()
        )
    )
    return primary_key_constraints[0] if primary_key_constraints else None


@cache
def _databricks_dialect_get_schema_constraints(
    connection: Connection,
    schema: str,
) -> dict[
    str,
    dict[
        str,
        dict[
            str,
            _ReflectedForeignKeyConstraint | _ReflectedPrimaryKeyConstraint,
        ],
    ],
]:
    contraint_types_tables_constraints: dict[
        str,
        dict[
            str,
            dict[
                str,
                _ReflectedForeignKeyConstraint
                | _ReflectedPrimaryKeyConstraint,
            ],
        ],
    ] = {}
    result: CursorResult = connection.execute(
        text(_CONSTRAINT_SELECT_STATEMENT),
        {"schema": schema},
    )
    row: Row
    for row in result:
        # Databricks stores constraints as uppercase, but the
        # metadata naming convention produces uppercase names,
        # so when reflecting we convert the names to uppercase to
        # produce correct matches for comparison
        if row.constraint_type not in contraint_types_tables_constraints:
            contraint_types_tables_constraints[row.constraint_type] = {}
        if (
            row.table_name
            not in contraint_types_tables_constraints[row.constraint_type]
        ):
            contraint_types_tables_constraints[row.constraint_type][
                row.table_name
            ] = {}
        if (
            row.constraint_name
            not in contraint_types_tables_constraints[row.constraint_type][
                row.table_name
            ]
        ):
            if row.constraint_type == "FOREIGN KEY":
                contraint_types_tables_constraints[row.constraint_type][
                    row.table_name
                ][row.constraint_name] = _ReflectedForeignKeyConstraint(
                    name=row.constraint_name,
                    constrained_columns=[row.column_name],
                    referred_schema=row.referenced_schema,
                    referred_table=row.referenced_table,
                    referred_columns=[row.referenced_column],
                )
            if row.constraint_type == "PRIMARY KEY":
                contraint_types_tables_constraints[row.constraint_type][
                    row.table_name
                ][row.constraint_name] = _ReflectedPrimaryKeyConstraint(
                    name=row.constraint_name,
                    constrained_columns=[row.column_name],
                )
        else:
            contraint_types_tables_constraints[row.constraint_type][
                row.table_name
            ][row.constraint_name]["constrained_columns"].append(
                row.column_name
            )
            if row.constraint_type == "FOREIGN KEY":
                cast(
                    "_ReflectedForeignKeyConstraint",
                    contraint_types_tables_constraints[row.constraint_type][
                        row.table_name
                    ][row.constraint_name],
                )["referred_columns"].append(row.referenced_column)
    return contraint_types_tables_constraints


@wraps(DatabricksDialect.get_foreign_keys)
def _databricks_dialect_get_foreign_keys(
    self: DatabricksDialect,
    connection: Connection,
    table_name: str,
    schema: str | None = None,
    **kwargs: Any,
) -> list[_ReflectedForeignKeyConstraint]:
    if not schema:
        schema = get_bind_database_schema(connection).schema
    if not schema:
        raise RuntimeError(repr(locals()))
    return (
        _databricks_dialect_get_schema_constraints(connection, schema)
        .get("FOREIGN KEY", {})
        .get(table_name, {})
        .values()
    )


_PRECISION_SCALE_PATTERN: re.Pattern = re.compile(r"DECIMAL\((\d+,\d+)\)")


@wraps(DatabricksDialect.get_columns)
def _databricks_dialect_get_columns(
    self: DatabricksDialect,
    connection: Connection,
    table_name: str,
    schema: str | None = None,
    **kwargs: Any,  # noqa: ARG001
) -> list[_ReflectedColumn]:
    """
    The provided `get_columns` method in the Databricks dialect
    does not have support for returning column information for columns
    that have precision and scale. This method overrides the default
    `get_columns` method to add support for columns with precision and
    scale.
    """
    # Pattern to extract the raw column type from the full type name
    # where the full name contains parenthesis (e.g. DECIMAL(38,4) -> decimal)
    raw_column_name_pattern: re.Pattern = re.compile(r"\w+")

    def _get_numeric_with_precision_and_scale(
        type_name: str,
    ) -> types.Numeric:
        """
        Given a type name with precision and scale,
        return a sqlalchemy.types.Numeric instance
        with the extracted precision and scale
        """
        precision_scale_match: re.Match | None = re.search(
            _PRECISION_SCALE_PATTERN, type_name
        )
        numeric: types.Numeric = types.Numeric()
        precision: int
        scale: int
        if precision_scale_match:
            precision, scale = map(
                int, precision_scale_match.group(1).split(",")
            )
            numeric = types.Numeric(precision=precision, scale=scale)
        return numeric

    databricks_connection: DatabricksConnection = (
        connection.connection  # type: ignore
    )
    databricks_cursor: Cursor = databricks_connection.cursor()
    columns_response: list[DatabricksRow] = databricks_cursor.columns(
        table_name=table_name,
        schema_name=schema,
        catalog_name=self.catalog,
    ).fetchall()
    column: DatabricksRow
    columns: list[_ReflectedColumn] = []
    for column in columns_response:
        raw_column_type_matched: re.Match | None = re.search(
            raw_column_name_pattern, column.TYPE_NAME
        )
        raw_column_type: str = column.TYPE_NAME
        if raw_column_type_matched:
            raw_column_type = raw_column_type_matched.group(0)
        raw_column_type = raw_column_type.lower()
        column_type: type[types.TypeEngine] | types.TypeEngine = (
            _GET_COLUMNS_TYPE_MAP[raw_column_type]
        )
        if raw_column_type == "decimal":
            column_type = _get_numeric_with_precision_and_scale(
                column.TYPE_NAME
            )
        if isinstance(column_type, type):
            column_type = column_type()
        columns.append(
            _ReflectedColumn(
                name=column.COLUMN_NAME,
                type=column_type,
                nullable=bool(column.NULLABLE),
                default=column.COLUMN_DEF,
            )
        )
    return columns


@wraps(DatabricksDialect.get_indexes)
def _databricks_dialect_get_indexes(
    self: DatabricksDialect,  # noqa: ARG001
    connection: Connection,  # noqa: ARG001
    table_name: str,  # noqa: ARG001
    schema: str | None = None,  # noqa: ARG001
    **kwargs: Any,  # noqa: ARG001
) -> list:
    """
    Indices aren't supported by Databricks, so always return
    an empty list.
    """
    return []


@cache
def patch_dialect() -> None:
    """
    This function patches the dialects to facilitate schema reflection
    """
    DatabricksDialect.get_pk_constraint = (  # type: ignore
        _databricks_dialect_get_pk_constraint  # type: ignore
    )
    DatabricksDialect.get_foreign_keys = (  # type: ignore
        _databricks_dialect_get_foreign_keys  # type: ignore
    )
    DatabricksDialect.get_indexes = (  # type: ignore
        _databricks_dialect_get_indexes  # type: ignore
    )
    DatabricksDialect.has_table = (  # type: ignore
        _databricks_dialect_has_table  # type: ignore
    )
    DatabricksDialect.get_columns = (  # type: ignore
        _databricks_dialect_get_columns  # type: ignore
    )


patch_dialect()

# endregion
