from __future__ import annotations

import argparse

from db_diagram._mermaid import (
    write_markdown,
    write_mermaid_images,
    write_mermaid_markdown,
)


def main() -> None:
    """
    This function is the entry point for the shell command
    `db-diagram`. See `db-diagram --help`
    for more information.
    """
    parser = argparse.ArgumentParser(
        prog="db-diagram",
        description=(
            "Write a markdown document with mermaid diagrams describing "
            "tables and relationships for the specified database URL"
        ),
    )
    parser.add_argument(
        "url",
        type=str,
        help=(
            "A [SQLAlchemy database URL](https://docs.sqlalchemy.org/en/20/"
            "core/engines.html#database-urls)"
        ),
    )
    parser.add_argument(
        "-mmd",
        "--mermaid-markdown",
        type=str,
        default="",
        help=(
            "A directory in which to write mermaid markdown (.mmd) documents. "
            "These documents will be named using the format "
            "`{TABLE_NAME}.mmd`."
        ),
    )
    parser.add_argument(
        "-svg",
        "--scalable-vector-graphics",
        type=str,
        default="",
        help=(
            "A directory in which to write SVG images. If this option "
            "is provided in concert with the --markdown / -md option, "
            "the markdown document will utilize the SVG images in lieu of "
            "embedding the mermaid diagrams. The SVG files will be named "
            "using the format `{TABLE_NAME}.mmd.svg`."
        ),
    )
    parser.add_argument(
        "-png",
        "--portable-network-graphics",
        type=str,
        default="",
        help=(
            "A directory in which to write PNG images. If this option "
            "is provided in concert with the --markdown / -md option, "
            "the markdown document will utilize the PNG images in lieu of "
            "embedding the mermaid diagrams. The PNG files will be named "
            "using the format `{TABLE_NAME}.mmd.png`."
        ),
    )
    parser.add_argument(
        "-md",
        "--markdown",
        type=str,
        default=None,
        help="The file path to which to write a markdown document",
    )
    parser.add_argument(
        "-cf",
        "--config-file",
        type=str,
        default=None,
        help="The path to a mermaid config file",
    )
    parser.add_argument(
        "-bc",
        "--background-color",
        type=str,
        default="transparent",
        help="A CSS background color for SVG diagrams",
    )
    parser.add_argument(
        "-t",
        "--theme",
        type=str,
        default="",
        help=(
            "default | neutral | dark | forest | base "
            "(only applicable for SVG/PNG images)"
        ),
    )
    parser.add_argument(
        "-i",
        "--include",
        default=[],
        action="append",
        help=(
            "Include only tables and views matching the specified pattern(s) "
            '(for example: "PREFIX_*")'
        ),
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        action="append",
        help=(
            "Exclude tables and views matching the specified pattern(s) "
            '(for example: "PREFIX_*")'
        ),
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1,
        help=(
            "Recursively traverse foreign key relationships up to this "
            "number of times"
        ),
    )
    namespace: argparse.Namespace = parser.parse_args()
    if namespace.mermaid_markdown:
        write_mermaid_markdown(
            namespace.url,
            directory=namespace.mermaid_markdown,
            include=tuple(namespace.include),
            exclude=tuple(namespace.exclude),
            depth=namespace.depth,
        )
    if namespace.scalable_vector_graphics:
        write_mermaid_images(
            namespace.url,
            directory=namespace.scalable_vector_graphics,
            image_format="svg",
            config_file=namespace.config_file,
            background_color=namespace.background_color,
            include=tuple(namespace.include),
            exclude=tuple(namespace.exclude),
            theme=namespace.theme,
            depth=namespace.depth,
        )
    if namespace.portable_network_graphics:
        write_mermaid_images(
            namespace.url,
            directory=namespace.portable_network_graphics,
            image_format="png",
            config_file=namespace.config_file,
            background_color=namespace.background_color,
            include=tuple(namespace.include),
            exclude=tuple(namespace.exclude),
            theme=namespace.theme,
            depth=namespace.depth,
        )
    if namespace.markdown:
        write_markdown(
            namespace.url,
            path=namespace.markdown,
            image_directory=(
                namespace.scalable_vector_graphics
                or namespace.portable_network_graphics
            ),
            image_format=(
                "svg" if namespace.scalable_vector_graphics else "png"
            ),
            include=tuple(namespace.include),
            exclude=tuple(namespace.exclude),
            depth=namespace.depth,
        )


if __name__ == "__main__":
    main()
