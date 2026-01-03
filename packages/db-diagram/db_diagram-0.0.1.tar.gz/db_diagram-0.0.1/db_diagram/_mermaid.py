"""
This module is a CLI and library for generating mermaid diagrams from
database metadata.

Example:

```mermaid
erDiagram
    a {
        integer A_ID PK
        string NAME
    }
    a_b {
        integer A_ID PK, FK
        integer B_ID PK, FK
        string NAME
    }
    a_b }o--|| a : "A_ID"
    a_b }o--|| b : "B_ID"
    a_b_c {
        integer A_ID PK, FK
        integer B_ID PK, FK
        integer C_ID PK, FK
        string NAME
    }
    a_b_c }o--|| a_b : "A_ID, B_ID"
    a_b_c }o--|| b_c : "B_ID, C_ID"
    b_c {
        integer B_ID PK, FK
        integer C_ID PK, FK
        string NAME
    }
    b_c }o--|| b : "B_ID"
    b_c }o--|| c : "C_ID"
    b {
        integer B_ID PK
        string NAME
    }
    c {
        integer C_ID PK
        string NAME
    }
```
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import suppress
from fnmatch import fnmatch
from itertools import chain
from operator import itemgetter
from pathlib import Path
from shutil import which
from subprocess import check_call
from typing import (
    TYPE_CHECKING,
    cast,
)

from sqlalchemy import URL, Column, Connection, Engine, MetaData
from sqlalchemy.sql.schema import (  # type: ignore
    Constraint,
    ForeignKey,
    ForeignKeyConstraint,
    Table,
)

from db_diagram._utilities import (
    as_cached_tuple,
    cache,
    get_bind_metadata,
    get_column_type_name,
    is_ci,
    iter_related_tables,
)

if TYPE_CHECKING:
    from collections.abc import Hashable, Iterable

with suppress(ImportError):
    # Patch the databricks dialect, if extras for that dialect are installed
    from db_diagram import _databricks  # noqa: F401


DEFAULT_CONFIG: dict[str, Hashable] = {
    # The default value would be 5000, which is too small for typical
    # entity relationship diagrams describing a database
    "maxTextSize": 99999999,
}


def quote(name: str) -> str:
    """
    Quote the specified name for use in a mermaid diagram.

    Parameters:
        name: The name to quote
    """
    return (
        f'"{name}"'
        if ("." in name) and not (name.startswith('"') and name.endswith('"'))
        else name
    )


def _iter_table_mermaid_entity(
    table: Table,
    include_tables: set[Table],
) -> Iterable[str]:
    """
    Yield lines defining the mermaid entity relationship diagram for the
    specified table.

    Parameters:
        table: The table at the "center" of the diagram (from which traversal
            begins)
        depth: The depth of the relationship graph to include
        include_tables:
    """
    yield f"    {quote(table.key)} {{"
    column_type: str
    key: str
    column: Column
    for column in table.columns:
        column_type = get_column_type_name(column)
        key = (
            " PK, FK"
            if column.foreign_keys and column.primary_key
            else (
                " PK"
                if column.primary_key
                else " FK"
                if column.foreign_keys
                else ""
            )
        )
        yield f"        {column_type} {column.name}{key}"
    yield "    }"
    # TODO: href
    # Once [this issue](https://github.com/mermaid-js/mermaid/issues/3966)
    # has been resolved/completed, uncomment the following 2 lines:
    # href_id: str = table_name.strip('"').replace(".", "").lower()
    # yield f'    click {table_name} href "#{href_id}" {table_name}'
    # Foreign Keys
    constraint: Constraint
    foreign_key: ForeignKey
    foreign_key_constraint: ForeignKeyConstraint
    for foreign_key_constraint in sorted(  # type: ignore
        filter(
            lambda constraint: isinstance(constraint, ForeignKeyConstraint),
            table.constraints or (),
        ),
        key=lambda foreign_key_constraint: (
            cast(
                "ForeignKeyConstraint",
                foreign_key_constraint,
            ).referred_table.name,
            cast(
                "ForeignKeyConstraint",
                foreign_key_constraint,
            ).column_keys,
        ),
    ):
        if foreign_key_constraint.referred_table not in include_tables:
            # Skip excluded tables
            continue
        column_names = ", ".join(foreign_key_constraint.column_keys)
        referred_table_name: str = foreign_key_constraint.referred_table.name
        referred_column_names: str = ", ".join(
            foreign_key.column.name
            for foreign_key in foreign_key_constraint.elements
        )
        table_name: str = quote(table.key)
        if column_names == referred_column_names:
            yield (
                f"    {table_name} }}o--|| {referred_table_name} : "
                f'"{column_names}"'
            )
        else:
            yield (
                f"    {table_name} }}o--|| {referred_table_name} : "
                f'"{column_names}:{referred_column_names}"'
            )


def _iter_table_mermaid_diagram(
    table: Table,
    depth: int | None = None,
) -> Iterable[str]:
    """
    Yield lines defining the mermaid diagram for a single table
    """
    related_tables: tuple[Table, ...] = tuple(
        iter_related_tables(table, depth=depth)
    )
    include_tables: set[Table] = set(related_tables) | {table}
    related_table: Table
    for related_table in chain((table,), related_tables):
        yield from _iter_table_mermaid_entity(
            related_table,
            include_tables=include_tables,
        )


def _get_table_mermaid_diagram(
    table: Table,
    depth: int | None = 1,
) -> str:
    """
    Return a mermaid entity relationship diagram for the specified class,
    including tables which are referenced in foreign key relationships to the
    specified depth.

    Parameters:
        cls: The class at the "center" of the diagram (from which traversal
            begins)
        depth: The depth of the relationship graph to include.
            If `depth == 0`, no limit will be placed on the depth of the graph.
    """
    mermaid_md: str = "\n".join(
        _iter_table_mermaid_diagram(table, depth=depth or None)
    )
    return f"erDiagram\n{mermaid_md}"


def _get_class_table_diagram(
    arguments: tuple[Table, int],
) -> tuple[str, str]:
    table: Table
    depth: int
    table, depth = arguments
    return table.key, _get_table_mermaid_diagram(table, depth=depth)


@as_cached_tuple()
def iter_tables_mermaid_diagrams(
    tables: MetaData | tuple[Table, ...] | Table,
    depth: int = 1,
    include: str | tuple[str, ...] = (),
    exclude: str | tuple[str, ...] = (),
) -> Iterable[tuple[str, str]]:
    """
    Yield a tuple containing a table name and the mermaid
    diagram for each table.

    Parameters:
        tables: Metadata or tables
        depth: The depth of the relationship graph to include in each
            diagram.
        include: Include only tables and views matching the
            specified pattern(s)
        exclude: Exclude tables and views matching the
            specified pattern(s)
    """
    if isinstance(include, str):
        include = (include,)
    if isinstance(exclude, str):
        exclude = (exclude,)
    if isinstance(tables, Table):
        tables = (tables,)
    if isinstance(tables, MetaData):
        tables = tuple(tables.sorted_tables)
    elif isinstance(tables, Table):
        tables = (tables,)
    table: Table
    pattern: str
    if include:
        tables = tuple(
            filter(
                lambda table: any(
                    fnmatch(
                        table.key,
                        pattern,
                    )
                    for pattern in include
                ),
                tables,
            )
        )
    if exclude:
        tables = tuple(
            filter(
                lambda table: not any(
                    fnmatch(
                        table.key,
                        pattern,
                    )
                    for pattern in exclude
                ),
                tables,
            )
        )
    class_count: int = len(tables)
    arguments: Iterable[tuple[Table, int]] = zip(
        tables,
        (depth,) * class_count,
        strict=False,
    )
    yield from sorted(
        ProcessPoolExecutor().map(_get_class_table_diagram, arguments)
    )


def write_markdown(  # noqa: C901
    metadata_source: (
        MetaData | Iterable[Table] | Table | str | URL | Engine | Connection
    ),
    path: Path | str,
    header_level: int = 2,
    title: str | None = None,
    depth: int = 1,
    image_directory: Path | str | None = None,
    image_format: str = "svg",
    include: str | tuple[str, ...] = (),
    exclude: str | tuple[str, ...] = (),
) -> None:
    """
    Write a markdown document, containing mermaid diagrams, for the
    specified metadata or tables, to the specified path.

    Parameters:
        metadata_source: SQLAlchemy metadata, tables, or a connection string
        path: The path to which to write the markdown document.
        title: The title of the markdown document. If not specified,
            the file name (sans extension) will be used as the title.
        depth: The depth of the relationship graph to include in each
            diagram
        include: Include only tables and views matching the
            specified pattern(s)
        exclude: Exclude tables and views matching the specified pattern(s)
    """
    if isinstance(metadata_source, (str, URL, Engine, Connection)):
        metadata_source = tuple(
            get_bind_metadata(metadata_source).tables.values()
        )
    if isinstance(metadata_source, Table):
        metadata_source = (metadata_source,)
    elif not isinstance(metadata_source, MetaData):
        metadata_source = tuple(metadata_source)
    header: str = "#" * header_level
    if isinstance(path, str):
        path = Path(path)
    if isinstance(image_directory, str) and image_directory:
        image_directory = Path(image_directory)
    if image_directory:
        image_directory = cast("Path", image_directory).relative_to(
            path.parent
        )
    if not title:
        title = path.stem
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="\n") as path_io:
        path_io.write(f"{header[:-1]} {title}\n")
        table_name: str
        mermaid_diagram: str
        tables_diagrams: tuple[tuple[str, str], ...] = (
            iter_tables_mermaid_diagrams(
                metadata_source,
                depth=depth,
                include=include,
                exclude=exclude,
            )
        )
        include_sub_header: bool = len(tables_diagrams) > 1
        for table_name, mermaid_diagram in tables_diagrams:
            if image_directory:
                if TYPE_CHECKING:
                    assert isinstance(image_directory, Path)
                image_path: str = str(
                    image_directory.joinpath(table_name)
                ).replace("\\", "/")
                path_io.write(
                    f"\n{header} {table_name}\n\n"
                    f"![{table_name}]"
                    f"({image_path}"
                    f".mmd.{image_format})\n"
                    if include_sub_header
                    else f"\n![{table_name}]"
                    f"({image_path}"
                    f".mmd.{image_format})\n"
                )
            else:
                path_io.write(
                    f"\n{header} {table_name}\n\n"
                    f"```mermaid\n"
                    f"{mermaid_diagram}\n"
                    "```\n"
                    if include_sub_header
                    else f"\n```mermaid\n{mermaid_diagram}\n```\n"
                )


def write_mermaid_markdown(
    metadata_source: (
        MetaData | Iterable[Table] | Table | str | URL | Engine | Connection
    ),
    directory: Path | str = "database",
    depth: int = 1,
    include: str | tuple[str, ...] = (),
    exclude: str | tuple[str, ...] = (),
) -> None:
    """
    Write mermaid markdown documents for the specified
    base class in the specified directory.

    Parameters:
        metadata_source: A SQLAlchemy database connection, connection string,
            metadata instance, or tables
        directory: The directory under which to which to write the
            mermaid markdown documents.
        depth: The depth of the relationship graph to include in each
            diagram
        include: Include only tables and views matching the
            specified pattern(s)
        exclude: Exclude tables and views matching the specified pattern(s)
    """
    if isinstance(metadata_source, (str, URL, Engine, Connection)):
        metadata_source = tuple(
            get_bind_metadata(metadata_source).tables.values()
        )
    if isinstance(metadata_source, MetaData):
        metadata_source = metadata_source.tables.values()
    elif isinstance(metadata_source, Table):
        metadata_source = (metadata_source,)
    if isinstance(directory, str):
        directory = Path(directory)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    for table_name, mermaid_diagram in iter_tables_mermaid_diagrams(
        metadata_source,
        depth=depth,
        include=include,
        exclude=exclude,
    ):
        path: Path = directory / f"{table_name}.mmd"
        with path.open("w", newline="\n") as path_io:
            path_io.write(mermaid_diagram)


def which_aa_exec() -> tuple[str, ...]:
    aa_exec: str | None = which("aa-exec")
    if aa_exec:
        return (aa_exec, "--profile=chrome")
    return ()


# NPM Install scripts obtained from
# https://nodejs.org/en/download

_POSIX_INSTALL_NPM: str = r"""
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
. "$HOME/.nvm/nvm.sh"
nvm install node
"""

_WINDOWS_INSTALL_NPM: str = r"""
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"
choco install nodejs
"""


@cache
def install_npm(*, force: bool = False) -> str:
    """
    Determine if `npm` is installed and return the command.

    Parameters:
        force: If True, force installation of npm even if it is already
            installed. For testing purposes only.
    """
    npm: str | None = which("npm")
    if npm and not force:
        return npm
    if not force:
        try:
            check_call((*which_aa_exec(), "npm", "--version"))
        except Exception:  # noqa: BLE001 S110
            pass
        else:
            return "npm"
    # Install node.js
    line: str
    if sys.platform.startswith("win"):
        for line in _WINDOWS_INSTALL_NPM.strip().splitlines():
            check_call(  # noqa: S602
                line,
                shell=True,
            )
    else:
        check_call(  # noqa: S602
            _POSIX_INSTALL_NPM.strip(),
            shell=True,
        )
    return which("npm") or "npm"


@cache
def install_mmdc() -> tuple[str, ...]:
    """
    Determine if `mmdc` is installed and return the command.
    """
    aa_exec: tuple[str, ...] = which_aa_exec()
    mmdc: str | None = which("mmdc")
    if mmdc:
        return (*aa_exec, mmdc)
    try:
        check_call(
            (
                *aa_exec,
                "mmdc",
                "--version",
            )
        )
    except Exception:  # noqa: BLE001
        check_call(
            (
                *aa_exec,
                which("npm") or "npm",
                "install",
                "-g",
                "@mermaid-js/mermaid-cli",
            )
        )
        return (*aa_exec, which("mmdc") or "mmdc")
    else:
        return (*aa_exec, "mmdc")


@cache
def _get_config_file(**kwargs: Hashable) -> str:
    """
    Create and return the path for a config file
    """
    # Remove any empty values
    kwargs = dict(filter(itemgetter(1), kwargs.items()))
    config: dict[str, Hashable] = DEFAULT_CONFIG.copy()
    config.update(kwargs)
    with tempfile.NamedTemporaryFile("w+t", delete=False) as file:
        json.dump(config, file)
    return file.name


def _write_image(
    arguments: tuple[str, str, Path, str, tuple[str, ...], str, str],
) -> None:
    table_name: str
    mermaid_diagram: str
    directory: Path
    config_file: str
    mmdc: tuple[str, ...]
    background_color: str
    image_format: str
    (
        table_name,
        mermaid_diagram,
        directory,
        config_file,
        mmdc,
        background_color,
        image_format,
    ) = arguments
    mmd_path: Path = directory / f"{table_name}.mmd"
    mmd_exists: bool = mmd_path.exists()
    if not mmd_exists:
        with mmd_path.open("w", newline="\n") as mmd_io:
            mmd_io.write(mermaid_diagram)
    svg_path: Path = directory / f"{table_name}.mmd.{image_format}"
    command: tuple[str, ...] = (
        *mmdc,
        "-i",
        str(mmd_path),
        "-o",
        str(svg_path),
    )
    if config_file:
        command += ("--configFile", config_file)
    if background_color:
        command += ("--backgroundColor", background_color)
    check_call(command)
    if not mmd_exists:
        mmd_path.unlink(missing_ok=True)


def write_mermaid_images(
    metadata_source: (
        MetaData | Iterable[Table] | Table | str | URL | Engine | Connection
    ),
    directory: str | Path,
    *,
    image_format: str = "svg",
    depth: int = 1,
    config_file: str | Path | None = None,
    background_color: str | None = "transparent",
    include: str | tuple[str, ...] = (),
    exclude: str | tuple[str, ...] = (),
    theme: str | None = None,
) -> None:
    """
    Write images for the specified class(es) in the specified directory.

    Parameters:
        metadata_source: A SQLAlchemy connection URL, engine, connection,
            or metadata from which to derive schema information
        directory:
            The directory under which to write the images.
        image_format: svg | png
        config_file: A path to a [mermaid config file](
            https://mermaid.js.org/config/schema-docs/config.html)
        background_color: A CSS background color
        depth: The depth of the relationship graph to include in each
            diagram
        include: Include only tables and views matching the
            specified pattern(s)
        exclude: Exclude tables and views matching the
            specified pattern(s)
        theme: default | neutral | dark | forest | base
    """
    if isinstance(metadata_source, (str, URL, Engine, Connection)):
        metadata_source = tuple(
            get_bind_metadata(metadata_source).tables.values()
        )
    if isinstance(metadata_source, Table):
        metadata_source = (metadata_source,)
    elif not isinstance(metadata_source, MetaData):
        metadata_source = tuple(metadata_source)
    mmdc: tuple[str, ...] = install_mmdc()
    if isinstance(directory, str):
        directory = Path(directory)
    if not config_file:
        config_file = _get_config_file(theme=theme)
    elif isinstance(config_file, Path):
        config_file = str(config_file)
    os.makedirs(directory, exist_ok=True)
    args: tuple[tuple[str, ...], ...]
    arguments: Iterable[tuple[str | Path | tuple | None, ...]] = (
        (*args, directory, config_file, mmdc, background_color, image_format)
        for args in iter_tables_mermaid_diagrams(
            metadata_source,
            depth=depth,
            include=include,
            exclude=exclude,
        )
    )
    max_workers: int | None = None
    if is_ci():
        # If running in a CI environment, limit the number of workers
        # to prevent excessive resource use
        max_workers = 1
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        deque(pool.map(_write_image, arguments), maxlen=0)
