from __future__ import annotations

import functools
import os
from itertools import chain
from typing import TYPE_CHECKING, Any, NamedTuple

from sqlalchemy import (
    Column,
    Connection,
    Engine,
    MetaData,
    create_engine,
    make_url,
)
from sqlalchemy.engine.url import URL
from sqlalchemy.sql.schema import Constraint, ForeignKeyConstraint, Table
from sqlalchemy.types import TypeDecorator, TypeEngine

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Iterable,
    )

any_lru_cache: Callable[..., Callable[..., Callable[..., Any]]] = (
    functools.lru_cache
)  # type: ignore
str_lru_cache: Callable[..., Callable[..., Callable[..., str]]] = (
    functools.lru_cache
)  # type: ignore

cache: Callable[[Callable], Callable]
try:
    from functools import cache  # type: ignore
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


def as_tuple(
    user_function: Callable[..., Iterable[Any]],
) -> Callable[..., tuple[Any, ...]]:
    """
    This is a decorator which will return an iterable as a tuple.
    """

    def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        return tuple(user_function(*args, **kwargs) or ())

    return functools.update_wrapper(wrapper, user_function)


def as_cached_tuple(
    maxsize: int | None = None, *, typed: bool = False
) -> Callable[[Callable[..., Iterable[Any]]], Callable[..., tuple[Any, ...]]]:
    """
    This is a decorator which will return an iterable as a tuple,
    and cache that tuple.

    Parameters:

    - maxsize (int|None) = None: The maximum number of items to cache.
    - typed (bool) = False: For class methods, should the cache be distinct for
      sub-classes?
    """
    return functools.lru_cache(maxsize=maxsize, typed=typed)(as_tuple)


def iter_referenced_tables(
    table: Table,
    exclude: Iterable[str] = (),
    depth: int | None = None,
) -> Iterable[Table]:
    """
    Yield all tables referenced by the given table, to a specified depth.

    Parameters:
        table:
        exclude: One or more table names to exclude
        depth: If provided, and greater than 1, recursive references
            will be included
    """
    if not isinstance(exclude, set):
        exclude = set(exclude)
    constraint: Constraint
    foreign_key_constraint: ForeignKeyConstraint
    for foreign_key_constraint in filter(  # type: ignore
        lambda constraint: isinstance(constraint, ForeignKeyConstraint),
        table.constraints or (),
    ):
        if TYPE_CHECKING:
            assert isinstance(foreign_key_constraint.referred_table, Table)
        key: str = str(foreign_key_constraint.referred_table.key)
        if (not exclude) or (key not in exclude):
            exclude.add(key)
            yield foreign_key_constraint.referred_table
            if (depth is None) or (depth > 1):  # pragma: no cover
                yield from iter_referenced_tables(
                    foreign_key_constraint.referred_table,
                    exclude,
                    (None if depth is None else depth - 1),
                )


def get_column_type_name(column: Column) -> str:
    column_type: (
        type[TypeEngine | TypeDecorator] | TypeEngine | TypeDecorator
    ) = column.type
    if not isinstance(column_type, type):
        column_type = type(column_type)
    if issubclass(column_type, TypeDecorator):  # pragma: no cover
        column_type = column_type.impl
        if not isinstance(column_type, type):
            column_type = type(column_type)
    visit_name: str = getattr(column_type, "__visit_name__", "") or ""
    return visit_name


@cache
def get_metadata_tables_referenced(
    metadata: MetaData,
) -> dict[Table, set[Table]]:
    """
    Obtain and cache a mapping of tables to the tables which they directly
    reference
    """
    tables_references: dict[Table, set[Table]] = {}
    table: Table
    for table in metadata.sorted_tables:
        if table not in tables_references:
            tables_references[table] = set()
        reference: Table
        for reference in iter_referenced_tables(table, depth=1):
            tables_references[table].add(reference)
    return tables_references


@cache
def get_metadata_tables_references(
    metadata: MetaData,
) -> dict[Table, set[Table]]:
    """
    Obtain and cache a mapping of tables to the other tables which directly
    referenced the table
    """
    references_tables: dict[Table, set[Table]] = {}
    table: Table
    references: set[Table]
    for table, references in get_metadata_tables_referenced(metadata).items():
        for reference in references:
            if reference not in references_tables:
                references_tables[reference] = set()
            references_tables[reference].add(table)
    return references_tables


def iter_related_tables(
    table: Table,
    depth: int | None = None,
    _used: Iterable[Table] = (),
) -> Iterable[Table]:
    """
    Yield all related tables up to the specified depth.
    """
    if not isinstance(_used, set):
        _used = set(_used)
    _used.add(table)
    related_table: Table
    for related_table in sorted(
        chain(
            get_metadata_tables_referenced(table.metadata).get(table, ()),
            get_metadata_tables_references(table.metadata).get(table, ()),
        ),
        key=lambda related_table: related_table.key,
    ):
        if related_table not in _used:
            yield related_table
            _used.add(related_table)
            if (depth is None) or (depth > 1):
                yield from iter_related_tables(
                    related_table,
                    depth=None if depth is None else depth - 1,
                    _used=_used,
                )


@cache
def is_ci() -> bool:
    return bool(
        # Github Actions
        ("CI" in os.environ and (os.environ["CI"].lower() == "true"))
        # Jenkins
        or ("HUDSON_URL" in os.environ)
    )


def get_table_primary_key_and_column_names(
    table: Table,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Return a 2-item tuple containing the primary key column names first,
    then the other column names.
    """
    primary_key_column_names: list[str] = []
    other_column_names: list[str] = []
    column: Column
    for column in table.columns:
        if column.primary_key:
            primary_key_column_names.append(column.name)
        else:
            other_column_names.append(column.name)
    return tuple(primary_key_column_names), tuple(other_column_names)


def get_bind_dialect_name(
    bind: Engine | Connection | str | URL | None,
) -> str:
    """
    Given a connectable `bind` (connection or engine) object, return the name
    of the dialect used (for example: "sqlite", "snowflake",
    or "postgresql").
    """
    dialect_name: str | bytes = "default"
    if isinstance(bind, URL):
        dialect_name = bind.drivername
    elif isinstance(bind, str):
        dialect_name = bind.partition("://")[0].partition("+")[0].lower()
    elif isinstance(bind, Engine):
        dialect_name = bind.dialect.name
    elif isinstance(bind, Connection):
        dialect_name = bind.engine.dialect.name
    if isinstance(dialect_name, bytes):
        dialect_name = dialect_name.decode("utf-8")
    return dialect_name.partition("+")[0].lower()


class DatabaseSchema(NamedTuple):
    database: str | None
    schema: str | None


def get_bind_database_schema(
    bind: Connection | Engine | URL | str,
) -> DatabaseSchema:
    """
    Returns the database and schema name from an engine, connection, connection
    URL, or connection string.
    """
    dialect_name: str = get_bind_dialect_name(bind)
    if dialect_name == "sqlite":
        return DatabaseSchema(None, None)
    url: URL = (
        bind.engine.url
        if isinstance(bind, Connection)
        else (
            bind.url
            if isinstance(bind, Engine)
            else (bind if isinstance(bind, URL) else make_url(bind))
        )
    )
    url_query_schema: tuple[str, ...] | str | None = url.query.get("schema")
    schema: str | None = (
        url_query_schema[0]
        if isinstance(url_query_schema, tuple)
        else url_query_schema
    )
    if dialect_name == "databricks":
        url_query_catalog: tuple[str, ...] | str | None = url.query.get(
            "catalog"
        )
        catalog: str | None = (
            url_query_catalog[0]
            if isinstance(url_query_catalog, tuple)
            else url_query_catalog
        )
        return DatabaseSchema(catalog, schema)
    if url.database:
        database: str
        database_schema: str
        database, _, database_schema = url.database.partition("/")
        if dialect_name == "snowflake":
            # Snowflake appends the schema to the database name
            schema = database_schema or schema or None
        elif not schema:
            schema = database_schema or None
        return DatabaseSchema(database, schema)
    return DatabaseSchema(None, schema)


def get_bind_metadata(bind: str | URL | Engine | Connection) -> MetaData:
    """
    Get SQLAlchemy metadata for a connection string, engine, or connection.
    """
    if isinstance(bind, (str, URL)):
        bind = create_engine(bind)
    metadata: MetaData = MetaData()
    bind_database_schema: DatabaseSchema = get_bind_database_schema(bind)
    metadata.reflect(bind=bind, views=True, resolve_fks=True)
    # Re-key `metadata.tables` so that catalog/database and schema names
    # are removed if they match the bind's database and schema
    table: Table
    for key, table in tuple(metadata.tables.items()):
        if table.schema and bind_database_schema.schema == table.schema:
            dict.__setitem__(metadata.tables, table.name, table)
            dict.__delitem__(metadata.tables, key)
            table.schema = None
    return metadata
