from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Annotated
from collections import defaultdict
from urllib.parse import urlparse

import click
import yaml
import html
import re

from pydantic import BaseModel, constr, AnyHttpUrl
from pydantic.types import ConstrainedStr

@click.command()
@click.option(
    "--input-dir",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    )
)
@click.option(
    "--output-dir",
    required=True,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=Path,
    )
)
def main(
    input_dir: Path,
    output_dir: Path,
) -> None:

    packages = find_packages(input_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    pkg_dirs = []

    for pkg, artifacts in packages.items():
        pkg_dirs.append(
            render_pkg_artifacts_index(output_dir, pkg, artifacts)
        )

    render_pkgs_index(output_dir, pkg_dirs)


def render_pkgs_index(output_dir: Path, pkg_dirs: list[Path]) -> None:
    anchors = []

    for p in sorted(pkg_dirs):
        rel_path = p.relative_to(output_dir)
        anchors.append(f'<a href="{rel_path}/">{p.name}</a>')

    index = "\n".join(
        ["<!DOCTYPE html>", "<html>", "<body>"] + anchors + ["</body>", "</html>"]
    )

    output_dir.joinpath("index.html").open("w").write(index)


def render_pkg_artifacts_index(
    output_dir: Path,
    pkg: str,
    artifacts: list[Artifact]
) -> Path:
    pkg_dir = output_dir.joinpath(normalize_package_name(pkg))
    pkg_dir.mkdir(parents=True, exist_ok=True)

    anchors = []

    for a in sorted(artifacts, key=lambda x: x.href):
        text = PurePosixPath(a.href.path or "").name or a.href

        href = urlparse(a.href)

        if a.sha256:
            href = href._replace(fragment=f"sha256={a.sha256}")

        if a.requires_python:
            python = html.escape(a.requires_python)
            requires = f' data-requires-python="{python}"'
        else:
            requires = ""

        anchors.append(f'<a href="{href.geturl()}"{requires}>{text}</a>')

    index = "\n".join(
        ["<!DOCTYPE html>", "<html>", "<body>"] + anchors + ["</body>", "</html>"]
    )

    pkg_dir.joinpath("index.html").open("w").write(index)

    return pkg_dir


def find_packages(loc: Path) -> dict[PackgeNameType, list[Artifact]]:
    packages = defaultdict(list)

    for file in loc.glob("**/*"):
        if file.suffix not in {".yaml", ".yml"}:
            continue

        for obj in yaml.safe_load_all(file.open("r")):
            a = Artifact.parse_obj(obj)
            packages[a.package].append(a)

    return packages


def normalize_package_name(name: str) -> str:
     return re.sub(r"[-_.]+", "-", name).lower()


def from_snake_to_camel(s: str) -> str:
    words = s.split("_")

    return f"{words[0]}{''.join(x.capitalize() for x in words[1:])}"


PackgeNameType = Annotated[
  ConstrainedStr,
  constr(regex="^([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9])$")
]

class Artifact(BaseModel):
    package: PackgeNameType
    href: AnyHttpUrl
    sha256: str | None = None
    requires_python: str | None = None

    class Config:
        alias_generator = from_snake_to_camel


if __name__ == "__main__":
    main()
